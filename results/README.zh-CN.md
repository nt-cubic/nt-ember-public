# 测试数据

[English](README.md) · **简体中文**

| 文件 | 粒度 | 内容 |
| --- | --- | --- |
| [quality/](quality/) | 原始逐样例 TSV | 5 份评分器输出，按样例 ID 保存 token 数、NLL、首 token 命中和贪心 LCP |
| [decode-microbench-runs.csv](decode-microbench-runs.csv) | 历史逐次测量摘录 | 28 token 提示、1,500 token 解码，记录各配置的三次测量与 token 来源 |
| [agent-hot-runs.csv](agent-hot-runs.csv) | 历史逐次测量摘录 | 内部工具调用合约，保留已记录的逐次热态速度与可用的全轮指标 |
| [performance-summary.csv](performance-summary.csv) | 历史汇总 | 精确档速度范围、14,392 token 预填充、追问及 Lite 短提示 |
| [routing-quality-summary.csv](routing-quality-summary.csv) | 历史汇总 | general 集的独立路由档位实验及相对精确档的 NLL 变化 |
| [long-context.csv](long-context.csv) | 历史汇总 | 约 32K–245K 提示下的预填充耗时、稳态解码与合成检索 |
| [dram-bandwidth.log](dram-bandwidth.log) | 原始日志 | 单机内存读与复制微测，单位 GB/s |

质量文件中的 `case_…` 是对应公开数据集的样例 ID。general 火种和两个 nt-llama 文件各 100 条。router 火种预填充文件为 106 条，nt-llama 文件为 112 条，比较时取共同样例。字段和配对结果见 [质量测试](../QUALITY.zh-CN.md)。

逐次测速 CSV 中的 `observation` 按已记录的逐组顺序编号。汇总文件中的 `low` 和 `high` 为记录中的区间边界，单值的两个边界相同，`aggregation` 标注观测范围、单值或均值。空字段代表原记录未提供该值。约 32K–245K 是提示长度标签。DRAM 的复制带宽按读写流量之和计量。

以上记录由项目在同一套 Windows 11 单 RTX 5090 主机上生成。发布的逐次摘录保留测量值及已知设置，内部对话正文、运行日志与时间戳未随摘录打包。独立 HTTP 复测格式见 [测试协议](../BENCHMARK.zh-CN.md)。
