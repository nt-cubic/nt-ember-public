# Standalone Benchmarks and Quality Summaries

**English** · [简体中文](README.zh-CN.md)

These scripts use the Python standard library and require Python 3.10 or later. Run the commands below from the repository root.

## HTTP benchmark

Start the server you want to test, then set `--base-url` to the API base URL and `--model` to the served model ID. The example uses port 8080. The server's `/v1/models` endpoint usually lists its model IDs.

```sh
python benchmark/run.py --base-url http://127.0.0.1:8080/v1 --model deepseek-v4.1-local --repeats 3 --output local-run.jsonl
```

By default, the script runs the [three short synthetic prompts](cases.jsonl) in order, with three consecutive requests per case. Use `--warmup 1` to send an unmeasured request before each case. Repeating a request can reuse the prefix. Check `cached_tokens` to see how much was reused. If the server rejects the streaming usage option, add `--no-stream-usage`.

Use `--cases path/to/cases.jsonl` to supply a custom workload. Each line needs a unique `id` and a `request` object with `messages`. The request may specify temperature, output limits, tools, or thinking parameters. The script sends streaming, single-sequence requests. For long-prompt or follow-up benchmarks, include the full conversation history in each request and arrange the cases in the intended cache order.

```json
{"id":"append","request":{"messages":[{"role":"user","content":"Give two uses of a compass."},{"role":"assistant","content":"Navigation and mapping."},{"role":"user","content":"Which use matters at sea?"}],"temperature":0,"max_tokens":128}}
```

Choose an output file that does not yet exist. The JSONL file records per-request counts, timings, finish reasons, or error types. Message text and model output are omitted. Standard output shows the median and the number of valid samples per case. Request errors produce a nonzero exit code, and completed records are available in the output file. [Measurement definitions](../BENCHMARK.md)

## Recalculate the quality table

```sh
python benchmark/quality_summary.py results/quality/general-nt-rerun.tsv results/quality/general-ember.tsv
python benchmark/quality_summary.py results/quality/general-nt-nofuse.tsv
python benchmark/quality_summary.py results/quality/router-nt-rerun.tsv results/quality/router-ember-prefill.tsv
python benchmark/quality_summary.py results/quality/router-nt-rerun.tsv
```

With one file, the script summarizes all cases. With two files, it matches cases by ID and checks prompt and target token counts. It then reports the metrics for each side, the NLL difference, and any cases unique to either file.
