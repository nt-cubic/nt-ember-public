# Measurement Data

**English** · [简体中文](README.zh-CN.md)

| File | Level of detail | Contents |
| --- | --- | --- |
| [quality/](quality/) | Raw per-case TSV | Five scorer outputs with token counts, NLL, first-token matches, and greedy LCP by case ID |
| [decode-microbench-runs.csv](decode-microbench-runs.csv) | Individual historical measurements | Three runs per configuration with a 28-token prompt and 1,500 decode tokens, with the token source identified |
| [agent-hot-runs.csv](agent-hot-runs.csv) | Individual historical measurements | Recorded warm decode speeds for the internal tool-calling benchmark and all-turn metrics where available |
| [performance-summary.csv](performance-summary.csv) | Historical summary | Exact-mode speed ranges, 14,392-token prefill, follow-up latency, and Lite short-prompt speed |
| [routing-quality-summary.csv](routing-quality-summary.csv) | Historical summary | Separate routing-mode experiment on general, with NLL change relative to Exact mode |
| [long-context.csv](long-context.csv) | Historical summary | Prefill times, steady-state decode speeds, and synthetic retrieval for prompts of about 32K–245K tokens |
| [dram-bandwidth.log](dram-bandwidth.log) | Raw log | Memory read and copy microbenchmarks on the workstation, in GB/s |

Identifiers of the form `case_…` match cases in the corresponding public dataset. The three general files contain 100 cases each. The router prefill file for EMBER contains 106 cases and the nt-llama router file contains 112. Comparisons use the shared cases. [Field definitions and paired results](../QUALITY.md)

The `observation` field in the individual-run CSVs follows the recorded order within each group. In the summary CSVs, `low` and `high` give the bounds of the recorded range. A single reported number appears in both fields. The `aggregation` field identifies a range, a single value, or a mean. Blank fields indicate unavailable values. The 32K–245K labels indicate approximate prompt lengths. DRAM copy bandwidth counts both read and write traffic.

The project measured these results on the same Windows 11 workstation with one RTX 5090. Individual-run extracts retain the recorded values and known settings. Conversation text, service logs, and timestamps are omitted from the extracts. [Standalone HTTP measurement protocol](../BENCHMARK.md)
