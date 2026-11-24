# Benchmark Protocol

**English** · [简体中文](BENCHMARK.zh-CN.md)

Historical results were measured on Windows 11 (WDDM) with one RTX 5090 (32 GB), a Ryzen 9 9950X3D, 128 GB of DDR5, and an NVMe SSD. The model was DeepSeek-V4.1-Flash-1017 in UD-IQ1_S. Requests ran one at a time.

## Workloads

| Workload | Input and configuration | Metric |
| --- | --- | --- |
| Decode microbenchmark | Start with a 28-token prompt and decode 1,500 tokens. EMBER's fed run uses a fixed token stream. nt-llama generates freely | Steady-state decode tokens/s, three observations, and their arithmetic mean. Keep the fixed-stream and free-generation labels when comparing results |
| Internal tool-calling agent benchmark | 10 turns with tools, thinking enabled, temperature 0.6, and no explicit output token cap. Context spans about 4K–15K tokens | Warm decode tokens/s over turns 2–10, with an all-turn result where available |
| Prefill | Natural 14,392-token prompt, model already loaded, and about 20.5 GiB of configured expert cache | Newly processed prompt tokens/s, reported as an observed range |
| Follow-up | Reuse a prefix and append 470 tokens | Time from sending the follow-up to first output |
| Long context | Prompts of about 32K, 64K, 128K, and 245K tokens in Exact mode with speculation off | Prefill latency, steady-state decode throughput over 400 tokens, and retrieval at specified depths |

The first publication includes available metrics from the internal tool-calling runs and fixed-stream benchmark. The original conversations, fixed token sequence, and complete service logs were omitted. [Available data and measurement detail](results/README.md)

## Standalone HTTP measurements

The [benchmark tools](benchmark/README.md) send streaming requests to a running local OpenAI-compatible Chat Completions server. They default to three synthetic short prompts and accept JSONL cases with long prompts or conversation history. The HTTP benchmark uses the metrics below. The historical microbenchmark and internal agent benchmark use the workloads specified above.

| Field | How it is measured |
| --- | --- |
| `ttft_ms` | Time from sending the request to the first SSE delta with answer text, reasoning, or a tool call. A role-only event does not count |
| `elapsed_ms` | Client time until the stream finishes, including queueing, transport, prefill, and decode |
| `prompt_tokens` / `cached_tokens` / `completion_tokens` | Server-side usage counts, with timing fields used as a fallback where available |
| `prompt_tps` / `decode_tps` | Server-reported prefill and decode throughput. Missing timing fields are reported as null |

## Comparison procedure

1. Record the engine version, model and quantization revision, OS and driver, VRAM and RAM, context limit, expert-cache configuration, routing mode, speculation, and sampling settings.
2. Keep other inference workloads off the GPU. Match the request content, chat template, sampling parameters, output cap, and concurrency.
3. Measure cold startup, a loaded model with a cold prefix, and prefix reuse separately. When comparing a first request with reuse of the same prefix, save the cached token count for each request. Restart the server before each cold-start measurement.
4. Keep at least three per-request records for each condition. Report the sample count and median, plus any errors or changes in the environment. Interleaving A/B runs can reduce the effect of machine state drifting over time.
5. Report the generated token count, finish reason, and availability of server timings. Label results with the applicable quantization, prompt length, speculation settings, and quality mode.
