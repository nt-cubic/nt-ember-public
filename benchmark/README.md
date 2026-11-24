# 独立测速与质量汇总

使用 Python 3.10 或以上版本，依赖标准库。以下命令从仓库根目录执行。

## HTTP 测速

先启动待测服务，再将 `--base-url` 和 `--model` 换成服务的 API 根路径和模型 ID。示例端口为 8080，模型 ID 通常可从服务的 `/v1/models` 获得。

```sh
python benchmark/run.py --base-url http://127.0.0.1:8080/v1 --model deepseek-v4.1-local --repeats 3 --output local-run.jsonl
```

默认顺序执行 [三条合成短提示](cases.jsonl)，每条连跑三次。`--warmup 1` 可在每条用例之前增加一次不计入统计的请求。重复输入可能命中缓存，使用 `cached_tokens` 检查复用情况。若服务拒绝流式 usage 参数，可添加 `--no-stream-usage`。

用 `--cases path/to/cases.jsonl` 指定自定义负载。每行含唯一的 `id` 和一个含 `messages` 的 `request` 对象。请求体可设温度、输出上限、工具或思考参数，脚本统一发送流式单序列请求。对照长提示或追问时，把完整消息历史放进各自的请求，并按预期的缓存顺序安排用例。

```json
{"id":"append","request":{"messages":[{"role":"user","content":"Give two uses of a compass."},{"role":"assistant","content":"Navigation and mapping."},{"role":"user","content":"Which use matters at sea?"}],"temperature":0,"max_tokens":128}}
```

输出路径应为尚未存在的文件。JSONL 逐请求保存计数、计时、停止原因或错误类型，不记录消息正文和模型输出。标准输出按用例给出中位数及有效样本数。出现请求错误时进程返回非零状态，已保存的行可用于排查。客户端测量口径见 [测试协议](../BENCHMARK.md)。

## 重算质量表

```sh
python benchmark/quality_summary.py results/quality/general-nt-rerun.tsv results/quality/general-ember.tsv
python benchmark/quality_summary.py results/quality/general-nt-nofuse.tsv
python benchmark/quality_summary.py results/quality/router-nt-rerun.tsv results/quality/router-ember-prefill.tsv
python benchmark/quality_summary.py results/quality/router-nt-rerun.tsv
```

单个文件汇总全部样例。两个文件先按样例 ID 配对，核对提示和目标 token 数，再计算两侧指标与 NLL 差，并列出各自独有的样例。
