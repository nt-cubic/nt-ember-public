# FAQ

**English** · [简体中文](FAQ.zh-CN.md)

## When will EMBER be open source?

We plan to open-source the EMBER inference engine once SSD weight streaming is ready and end-to-end testing with a full 1M-token context is complete. The current public materials include the technical report, standalone benchmark and scoring-summary scripts, and measurement data. To discuss distribution or integration, contact the maintainer. [Technical discussion and collaboration](CONTACT.md)

## Which platforms and models have been tested?

The published results cover Windows 11 (WDDM), one RTX 5090 (32 GB), 128 GB of RAM, and DeepSeek-V4.1-Flash-1017 in UD-IQ1_S. Fast, Faster, and Turbo have their own speed and quality results. Linux, multiple GPUs, other GPU models, other quantizations or models, and concurrent users are outside the scope of this validation.

## What does Exact mode mean?

Exact mode selects experts according to the model's scores and preserves the precision of the quantized weights and the F16 KV cache. When exact speculative decoding is enabled, the target model verifies proposed drafts. Exact mode in this report uses UD-IQ1_S weights. Bitwise agreement across engines depends on their numerical implementations. [Quality evaluation](QUALITY.md)

## Which clients can connect?

EMBER implements OpenAI-compatible `/v1/chat/completions` with streaming, non-streaming, and tool calls, plus `/v1/models`. Check that the server supports the endpoints and request fields your client uses. The public benchmark script can connect to a running server that supports streaming Chat Completions. Additional counters depend on the server. [Benchmark protocol](BENCHMARK.md)

## What does 256K mean?

256K is the configured limit of 262,144 tokens, shared by the chat template, prompt, and generated output. The published retrieval and decode measurements include prompts of about 245K tokens. [Technical report](PUBLIC-TECH-REPORT.md)

## What does offline operation require?

Prepare the engine, weights, and dependencies locally and use tools that can run on the same machine. Inference runs locally. Third-party weights and data are subject to their upstream license terms. [Technical report](PUBLIC-TECH-REPORT.md)
