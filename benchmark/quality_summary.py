"""Summarize or pair per-case continuation scores from TSV files."""

import argparse
import csv
import json
import math
from pathlib import Path
import sys


REQUIRED_FIELDS = {"id", "prompt_tokens", "target_tokens", "nll", "first_match", "greedy_lcp"}


def load_scores(path):
    rows = {}
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if not REQUIRED_FIELDS.issubset(reader.fieldnames or ()):
            raise ValueError(f"{path}: missing score columns")
        for row in reader:
            case_id = row["id"]
            try:
                prompt = int(row["prompt_tokens"])
                target = int(row["target_tokens"])
                nll = float(row["nll"])
                first = int(row["first_match"])
                lcp = int(row["greedy_lcp"])
                if (not case_id or case_id in rows or None in row or prompt < 0 or target <= 0
                        or not math.isfinite(nll) or nll < 0 or first not in (0, 1)
                        or not 0 <= lcp <= target):
                    raise ValueError
            except (ValueError, TypeError) as exc:
                raise ValueError(f"{path}:{reader.line_num}: invalid or duplicate score row") from exc
            rows[case_id] = (prompt, target, nll, first, lcp)
    if not rows:
        raise ValueError(f"{path}: no score rows")
    return rows


def summarize(rows):
    target_tokens = sum(row[1] for row in rows)
    return {
        "cases": len(rows),
        "target_tokens": target_tokens,
        "max_prompt_tokens": max(row[0] for row in rows),
        "avg_nll": math.fsum(row[2] for row in rows) / target_tokens,
        "first_matches": sum(row[3] for row in rows),
        "avg_greedy_lcp": sum(row[4] for row in rows) / len(rows),
    }


def compare(baseline, candidate):
    shared = sorted(baseline.keys() & candidate.keys())
    if not shared:
        raise ValueError("no shared case IDs")
    for case_id in shared:
        if baseline[case_id][:2] != candidate[case_id][:2]:
            raise ValueError(f"token counts differ for case {case_id!r}")
    left = summarize([baseline[case_id] for case_id in shared])
    right = summarize([candidate[case_id] for case_id in shared])
    return {
        "baseline_only_cases": sorted(baseline.keys() - candidate.keys()),
        "candidate_only_cases": sorted(candidate.keys() - baseline.keys()),
        "baseline": left,
        "candidate": right,
        "delta_nll": right["avg_nll"] - left["avg_nll"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path, nargs="?")
    args = parser.parse_args()
    try:
        baseline = load_scores(args.baseline)
        if args.candidate is None:
            result = summarize(list(baseline.values()))
        else:
            result = compare(baseline, load_scores(args.candidate))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
