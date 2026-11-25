# Why EMBER Is Fast

**English** · [简体中文](WHY-FASTER.zh-CN.md)

On the Windows 11 test workstation, the routed expert weights for DeepSeek-V4.1-Flash-1017 in UD-IQ1_S take up about 107 GiB. The RTX 5090 has 32 GB of VRAM, which also serves attention, KV state, and temporary buffers. Decode throughput depends on how many of the selected experts are already in VRAM and how quickly the engine can finish the remaining work.

## Decode overlaps cache hits, CPU compute, and PCIe transfers

During decoding, GPU work on cached experts overlaps with CPU execution and on-demand transfers for experts outside the cache. CPU reads and PCIe transfers share host memory bandwidth, so the throughput of each path depends on the work happening on the other.

Computing a miss in place on the CPU saves a PCIe transfer. Transferring an expert to the GPU uses PCIe bandwidth now and can avoid further transfers when that expert is reused. The measured configuration holds the expert weights in RAM. Its SSD serves Engram lookups. Streaming routed expert weights from SSD is a separate milestone. [Expert placement and hardware measurements](PUBLIC-TECH-REPORT.md#expert-placement-during-decode)

## Decode benchmark

EMBER averaged **67.8 tokens/s** over three runs with a fixed input stream of 1,500 decode tokens, exact routing, and speculative decoding off. The nt-llama reference averaged 32.2 tokens/s with free greedy generation, where the resulting output can change the expert access pattern. [Recorded runs](results/decode-microbench-runs.csv) · [Benchmark protocol](BENCHMARK.md)

## Expert-loading trade-offs

The benefit of caching an expert depends on how often it is selected again and how much VRAM is available after accounting for the conversation. Exact mode keeps the router's expert choices. Optional speed modes can change those choices during decode. Turbo averaged 83.8 tokens/s over two historical tool-calling runs. In a separate quality sweep, its NLL on general was about 2.4% above Exact mode. [Tool-calling measurements](results/agent-hot-runs.csv) · [Routing quality results](results/routing-quality-summary.csv)

## VRAM follows context length

A short conversation can leave more VRAM available for resident experts. As the conversation grows, the KV cache claims more of that budget, which can increase expert cache misses. A context reset returns the extra capacity to the expert cache. [Dynamic KV cache](PUBLIC-TECH-REPORT.md#dynamic-kv-cache)

## Prefill and follow-up turns use different paths

Prefill overlaps weight transfers with GPU computation. The measured 14,392-token prompt ran at 2,824–3,069 tokens/s with the model loaded. For a follow-up, EMBER can reuse a matching prefix and process the remaining tokens. A follow-up adding 470 tokens took 1.90–1.95 s to first output. [Performance measurements](results/performance-summary.csv)
