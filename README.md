# EMBER

**English** · [简体中文](README.zh-CN.md)

> When the grid goes dark, the ember still thinks.

EMBER is an offline inference engine for a single user. It runs the UD-IQ1_S quantization of DeepSeek-V4.1-Flash-1017 on one Windows 11 workstation with an RTX 5090 (32 GB VRAM) and 128 GB of system RAM. Once the model and runtime dependencies are in place, inference runs entirely on the local machine.

This repository publishes the technical report, benchmark protocol, standalone tools, and measurement records. We plan to open-source the EMBER engine after we finish work on streaming weights from SSD and complete end-to-end testing with a full 1M-token context. [Open-source plans and compatibility](FAQ.md)

**Technical questions and collaboration** · [ntcubic@gmail.com](mailto:ntcubic@gmail.com)

## How EMBER works

- **CPU and GPU decode together.** The GPU computes cached experts while other experts are computed directly from RAM on the CPU or transferred over PCIe for GPU execution.
- **Experts move to VRAM on demand.** The measured configuration keeps the roughly 107 GiB of routed expert weights in system RAM and caches recently used experts in VRAM. Computing a miss on the CPU saves a transfer. Moving it to the GPU can speed up execution and make the expert available for reuse. SSD streaming of expert weights is a separate milestone.
- **KV and expert weights share a VRAM budget.** Short conversations leave more room for experts. The KV cache grows as the conversation length increases, and a context reset returns that capacity to the expert cache. [Dynamic KV cache](PUBLIC-TECH-REPORT.md#dynamic-kv-cache)
- **Prefill overlaps transfers with GPU computation.** Follow-up turns can reuse a matching prefix and process only the remaining tokens.
- **Speculation and routing have separate quality controls.** Exact mode can verify DSpark or suffix drafts with the target model. The optional speed modes change expert selection or skip some low-weight experts during decode. [Quality evaluation](QUALITY.md)

The performance discussion covers the trade-offs between CPU execution, expert reuse, and long-context memory. [Why EMBER is fast](WHY-FASTER.md)

## Single-workstation results

### Short-prompt generation by output type

Turbo mode, greedy decoding, one RTX 5090.

| Output type | Decode throughput |
| --- | ---: |
| Tables | **127 tokens/s** |
| JSON | 112 tokens/s |
| Code | 88–95 tokens/s |
| Prose | 66–67 tokens/s |

### Long-context decoding

On the same Windows 11 workstation with one RTX 5090 and 128 GB of RAM, EMBER reached **45.4 tokens/s** over 400 steady-state decode tokens after a prompt of about 245K tokens. This run used Exact mode with speculative decoding off. At the same prompt length, the synthetic retrieval test passed at all three tested depths. [Long-context measurement summary](results/long-context.csv)

### Agent and prefill workloads

| Workload | EMBER result |
| --- | --- |
| 10 turns with tool calls and sampling, warm decode over turns 2–10 | 58–64 tokens/s in Exact mode. Turbo averaged 83.8 tokens/s across two runs |
| 14,392-token prompt with the model already loaded | 2,824–3,069 prefill tokens/s |
| 470 new tokens appended to a reused context | 1.90–1.95 s to first output |

These measurements come from internal runs. [Benchmark protocol](BENCHMARK.md) · [Available data and measurement detail](results/README.md)

## Documentation

- [Public technical report](PUBLIC-TECH-REPORT.md) — hardware constraints, CPU/GPU work sharing, long context, and performance trade-offs.
- [Benchmark protocol](BENCHMARK.md) — performance metrics, workloads, and comparison procedure.
- [Quality evaluation](QUALITY.md) — per-case NLL, long-context retrieval, and what the published results cover.
- [Standalone benchmark scripts](benchmark/README.md) — test a local Chat Completions server with Python's standard library.
- [Measurement data](results/README.md) — per-case scores, individual measurements, and historical summaries.
- [FAQ](FAQ.md) · [Technical discussion and collaboration](CONTACT.md)
