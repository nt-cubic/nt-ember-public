# 火种 EMBER

[English](README.md) · **简体中文**

> 断网断电，火种不灭。
>
> *When the grid goes dark, the ember still thinks.*

火种是面向单用户的离线推理引擎。它以一台 Windows 11 工作站为目标，在单张 RTX 5090（32 GB 显存）和 128 GB 系统内存上运行 DeepSeek-V4.1-Flash-1017 的 UD-IQ1_S 量化版。模型和运行依赖准备齐全后，推理可在本机离线完成。

这个仓库发布技术报告、测试方法、独立基准工具与可公开的测量记录。火种引擎采用闭源发布范围，兼容性见 [FAQ](FAQ.zh-CN.md)。

## 单机实测

| 场景 | 火种结果 |
| --- | --- |
| 10 轮工具调用与采样，取第 2–10 轮热态解码 | 精确档 58–64 token/s，Turbo 档两次均值 83.8 token/s |
| 14,392 token 提示，模型已加载 | 预填充 2,824–3,069 token/s |
| 复用上下文后追加 470 token | 首次输出 1.90–1.95 s |
| 约 245K token 长提示，精确档且关闭投机解码 | 400 token 稳态解码 45.4 token/s，三个检索深度均通过 |

这些数字来自项目内部实测。各场景的设置、数据粒度与复测条件见 [测试协议](BENCHMARK.zh-CN.md) 和 [结果索引](results/README.zh-CN.md)。

## 材料

- [公开技术报告](PUBLIC-TECH-REPORT.zh-CN.md) — 资源约束、CPU/GPU 分工、长上下文和速度取舍。
- [测试协议](BENCHMARK.zh-CN.md) — 性能指标、负载定义与对照方法。
- [质量测试](QUALITY.zh-CN.md) — 逐样例 NLL、长上下文检索与可核算范围。
- [独立测速脚本](benchmark/README.zh-CN.md) — 使用 Python 标准库测试本地 Chat Completions 服务。
- [测试数据](results/README.zh-CN.md) — 原始逐样例分数、逐次速度摘录和历史汇总。
- [FAQ](FAQ.zh-CN.md) · [技术交流与合作](CONTACT.zh-CN.md)
