# EMBER

**English** · [简体中文](README.zh-CN.md)

> When the grid goes dark, the ember still thinks.

EMBER is an offline inference engine for a single user. It runs the UD-IQ1_S quantization of DeepSeek-V4.1-Flash-1017 on one Windows 11 workstation with an RTX 5090 (32 GB VRAM) and 128 GB of system RAM. Once the model and runtime dependencies are in place, inference runs entirely on the local machine.

This repository publishes the technical report, benchmark protocol, standalone tools, and measurement records. The EMBER engine is closed source. [Compatibility and availability](FAQ.md)

## Single-workstation results

| Workload | EMBER result |
| --- | --- |
| 10 turns with tool calls and sampling, warm decode over turns 2–10 | 58–64 tokens/s in Exact mode. Turbo averaged 83.8 tokens/s across two runs |
| 14,392-token prompt with the model already loaded | 2,824–3,069 prefill tokens/s |
| 470 new tokens appended to a reused context | 1.90–1.95 s to first output |
| About 245K prompt tokens, Exact mode with speculative decoding off | 45.4 tokens/s over 400 steady-state decode tokens. Retrieval passed at all three tested depths |

These measurements come from internal runs. [Benchmark protocol](BENCHMARK.md) · [Available data and measurement detail](results/README.md)

## Documentation

- [Public technical report](PUBLIC-TECH-REPORT.md) — hardware constraints, CPU/GPU work sharing, long context, and performance trade-offs.
- [Benchmark protocol](BENCHMARK.md) — performance metrics, workloads, and comparison procedure.
- [Quality evaluation](QUALITY.md) — per-case NLL, long-context retrieval, and what the published results cover.
- [Standalone benchmark scripts](benchmark/README.md) — test a local Chat Completions server with Python's standard library.
- [Measurement data](results/README.md) — per-case scores, individual measurements, and historical summaries.
- [FAQ](FAQ.md) · [Technical discussion and collaboration](CONTACT.md)
