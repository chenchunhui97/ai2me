# 推理引擎与调度实验

对应 T10～T13、T18、T21。每次阅读固定仓库 URL 和 commit，调用图引用真实符号；源代码走读使用 [源码模板](../../templates/source-reading.md)。

顺序：nano-vLLM 全链路 → CPU KV block/scheduler 原型 → vLLM 请求追踪与改动 → SGLang 对照 → PD 原型或真实实验。patch、复现命令和运行日志摘要保存在本目录，静态分析、CPU 模拟与真实引擎性能结论分别标明。
