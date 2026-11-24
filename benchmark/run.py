"""Measure an existing OpenAI-compatible Chat Completions endpoint."""

import argparse
from datetime import datetime, timezone
from http.client import HTTPException
import json
import math
from pathlib import Path
import re
from statistics import median
import sys
from time import perf_counter
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


METRICS = ("ttft_ms", "elapsed_ms", "prompt_tps", "decode_tps")


def load_cases(path):
    cases = {}
    with path.open(encoding="utf-8-sig") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError as exc:
                raise ValueError(f"line {line_number}: invalid JSON") from exc
            name = row.get("id") if isinstance(row, dict) else None
            if not isinstance(name, str) or not re.fullmatch(r"[a-zA-Z0-9_.-]{1,64}", name):
                raise ValueError(f"line {line_number}: expected an ASCII case id")
            if name in cases:
                raise ValueError(f"line {line_number}: duplicate case id {name!r}")
            body = row.get("request")
            if not isinstance(body, dict) or not isinstance(body.get("messages"), list) or not body["messages"]:
                raise ValueError(f"line {line_number}: expected request.messages")
            try:
                json.dumps(body, allow_nan=False)
            except ValueError as exc:
                raise ValueError(f"line {line_number}: non-finite request value") from exc
            cases[name] = body
    if not cases:
        raise ValueError("no cases found")
    return cases


def sse_data(stream):
    data = []
    for raw in stream:
        line = raw.rstrip(b"\r\n")
        if not line:
            if data:
                yield b"\n".join(data)
                data.clear()
            continue
        field, _, value = line.partition(b":")
        if field == b"data":
            data.append(value.removeprefix(b" "))
    if data:
        yield b"\n".join(data)


def count(value):
    if type(value) is int and value >= 0:
        return value
    return None


def rate(value):
    if type(value) in (int, float) and math.isfinite(value) and value >= 0:
        return value
    return None


def read_stream(stream, start):
    first = None
    finish_reason = None
    done = False
    usage, timings = {}, {}
    for data in sse_data(stream):
        if data.strip() == b"[DONE]":
            done = True
            break
        event = json.loads(data)
        if not isinstance(event, dict) or event.get("error"):
            raise ValueError("invalid SSE response")
        if isinstance(event.get("usage"), dict):
            usage.update(event["usage"])
        if isinstance(event.get("timings"), dict):
            timings.update(event["timings"])
        for choice in event.get("choices") or []:
            if not isinstance(choice, dict):
                raise ValueError("invalid SSE choice")
            delta = choice.get("delta") or {}
            if not isinstance(delta, dict):
                raise ValueError("invalid SSE delta")
            if first is None and any(delta.get(key) for key in (
                "content", "reasoning_content", "reasoning", "tool_calls", "function_call", "refusal"
            )):
                first = perf_counter()
            reason = choice.get("finish_reason")
            if isinstance(reason, str) and re.fullmatch(r"[a-z_]{1,40}", reason):
                finish_reason = reason
    if not done and finish_reason is None:
        raise EOFError("stream ended before its terminal event")

    prompt = count(usage.get("prompt_tokens"))
    completion = count(usage.get("completion_tokens"))
    details = usage.get("prompt_tokens_details")
    cached = count(details.get("cached_tokens")) if isinstance(details, dict) else None
    if cached is None:
        cached = count(timings.get("cache_n"))
    prompt_new = count(timings.get("prompt_n"))
    if prompt is None and prompt_new is not None and cached is not None:
        prompt = prompt_new + cached
    return {
        "ttft_ms": round((first - start) * 1000, 3) if first is not None else None,
        "prompt_tokens": prompt,
        "cached_tokens": cached,
        "completion_tokens": completion if completion is not None else count(timings.get("predicted_n")),
        "prompt_tps": rate(timings.get("prompt_per_second")),
        "decode_tps": rate(timings.get("predicted_per_second")),
        "finish_reason": finish_reason,
    }


def measure(args, body):
    payload = dict(body, model=args.model, stream=True, n=1)
    if args.no_stream_usage:
        payload.pop("stream_options", None)
    else:
        payload["stream_options"] = {"include_usage": True}
    request = Request(
        args.base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload, allow_nan=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
    )
    start = perf_counter()
    try:
        with urlopen(request, timeout=args.timeout) as response:
            if response.headers.get_content_type() != "text/event-stream":
                raise ValueError("expected an SSE response")
            row = read_stream(response, start)
    except HTTPError as exc:
        row = {"error": f"HTTP_{exc.code}"}
        exc.close()
    except EOFError:
        row = {"error": "incomplete_stream"}
    except (ValueError, TypeError):
        row = {"error": "invalid_stream"}
    except (URLError, OSError, HTTPException):
        row = {"error": "connection_or_timeout"}
    row["elapsed_ms"] = round((perf_counter() - start) * 1000, 3)
    return row


def summarize(rows):
    successful = [row for row in rows if "error" not in row]
    summary = {"requests": len(rows), "errors": len(rows) - len(successful)}
    for key in METRICS:
        values = [row[key] for row in successful if row[key] is not None]
        summary[key] = {"samples": len(values), "median": median(values) if values else None}
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8080/v1")
    parser.add_argument("--model", required=True, help="served model ID")
    parser.add_argument("--cases", type=Path, default=Path(__file__).with_name("cases.jsonl"))
    parser.add_argument("--output", type=Path, required=True, help="new JSONL output file")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=0, help="unrecorded requests per case")
    parser.add_argument("--timeout", type=float, default=600, help="socket timeout in seconds")
    parser.add_argument("--no-stream-usage", action="store_true")
    args = parser.parse_args()
    try:
        base = urlsplit(args.base_url)
        if (base.scheme not in ("http", "https") or not base.hostname or
                base.username is not None or base.query or base.fragment):
            raise ValueError("expected an HTTP(S) base URL ending before /chat/completions")
        if args.repeats < 1 or args.warmup < 0 or not math.isfinite(args.timeout) or args.timeout <= 0:
            raise ValueError("repeats and timeout must be positive, warmup must be non-negative")
        cases = load_cases(args.cases)
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            results = {}
            for name, body in cases.items():
                for _ in range(args.warmup):
                    warmup = measure(args, body)
                    if "error" in warmup:
                        print(f"{name}: warmup failed ({warmup['error']})", file=sys.stderr)
                        return 1
                rows = []
                for repeat in range(1, args.repeats + 1):
                    utc = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
                    row = dict(measure(args, body), case=name, repeat=repeat, started_at_utc=utc)
                    output.write(json.dumps(row, allow_nan=False) + "\n")
                    output.flush()
                    rows.append(row)
                results[name] = summarize(rows)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(results, indent=2, allow_nan=False))
    return int(any(result["errors"] for result in results.values()))


if __name__ == "__main__":
    sys.exit(main())
