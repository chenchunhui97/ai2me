# 学习时间线

由 `learning/curriculum.json`、`profile.json` 和学习事件生成；修改计划后运行 `python3 scripts/study.py render`。

起始日期：**2026-11-07**；预算：每周 **10～15 小时**（尚待确认）。日期是建议，完成状态以真实验收为准。

前两周优先完成可独立实现、可计算、可验证的模型基础。每次安排约 10 分钟回忆、15～25 分钟理解、30～60 分钟独立实践和 10 分钟记录；按实际时间拆分。

## 第 1 周：模型实现基础（2026-11-07 ～ 2026-11-13）

| ID / 计划日期 | 任务 | 验收条件 | 成果位置 | 状态 |
|---|---|---|---|---|
| T01<br>2026-11-07 ～ 2026-11-08 | Attention 张量形状与能力诊断 | 不看答案写出 X、Wq/Wk/Wv、Q/K/V、scores、输出的形状，说明每一步运算及广播。<br>独立完成 B=1,S=1024,H=2048,Qheads=16,KVheads=4,d=128 的形状题，并完成 B=2,S=17 的变式。<br>明确记录哪些步骤独立完成、哪些需要提示；用小张量代码验证形状，不计为掌握完整 Attention。 | [my_knowledge/attention](../my_knowledge/attention/) | 学习中 |
| T02<br>2026-11-09 ～ 2026-11-10 | 单头 Attention、稳定 Softmax 与 causal mask | 用 PyTorch 基础张量运算实现单头 causal attention，不调用现成 attention 接口。<br>解释缩放项、稳定 Softmax、mask 位置与广播；用固定随机种子和参考实现比较输出误差。<br>覆盖长度 1、非整齐长度和未来 token 扰动不影响先前输出的用例。 | [labs/01-attention](../labs/01-attention/) | 未开始 |
| T03<br>2026-11-11 ～ 2026-11-13 | Multi-Head Attention 与形状变换 | 独立实现 QKV 投影、split heads、Attention、merge heads 与输出投影。<br>解释 transpose/reshape/contiguous、权重布局，完成不同 batch/长度的正确性对齐。<br>复盘本周至少一个具体错误，脱离参考重写核心计算。 | [labs/01-attention](../labs/01-attention/) | 未开始 |

周末：按 [复盘模板](../templates/weekly-review.md) 记录独立成果、卡点、到期复习和下周调整。

## 第 2 周：KV Cache 与完整计算链路（2026-11-14 ～ 2026-11-20）

| ID / 计划日期 | 任务 | 验收条件 | 成果位置 | 状态 |
|---|---|---|---|---|
| T04<br>2026-11-14 ～ 2026-11-15 | GQA/MQA 与 KV head 映射 | 在 MHA 实现上加入 GQA/MQA，解释 Query heads 与 KV heads 的分组关系。<br>对齐一个可信参考；说明逻辑 KV 扩展与真正物理复制的区别，计算 KV 节省比例。 | [labs/01-attention](../labs/01-attention/) | 未开始 |
| T05<br>2026-11-16 ～ 2026-11-17 | KV Cache 与 Prefill/Decode 正确性 | 实现 Prefill、逐 token Decode、位置偏移和 KV 追加，比较全序列重算与缓存推理 logits。<br>覆盖长度 1、不同起始位置、多个 decode 步和非零 past length 的 mask。<br>独立推导 24 层、4 KV heads、d=128、FP16 时每 token 48 KiB、1024 tokens 48 MiB 的 KV 占用并说明假设。 | [labs/01-attention](../labs/01-attention/) | 未开始 |
| T06<br>2026-11-18 ～ 2026-11-19 | RMSNorm、RoPE、SwiGLU 与小型 Decoder | 用随机权重组成带残差连接的小型 Decoder，解释 RMSNorm、RoPE 及 SwiGLU 的计算与形状。<br>在 torch.inference_mode 下验证全序列和缓存解码 logits；说明 dropout、位置、mask 的一致性条件。<br>保留运行环境、执行命令、误差阈值与结果；不要求训练出有用模型。 | [labs/02-mini-decoder](../labs/02-mini-decoder/) | 未开始 |
| T07<br>2026-11-20 ～ 2026-11-20 | 参数量、FLOPs 与显存账本 | 逐项计算 QKV/O、MLP 的参数量和矩阵乘法 FLOPs，声明乘加按 2 FLOPs 计算。<br>区分 Prefill/Decode、权重/KV/临时激活；分别写出 QK 和 AV 的计算量，解释因果与实现口径。<br>输出可运行计算脚本，对比小模型张量 numel 和估算；不把 tensor 大小等同于 allocator 总占用。 | [my_knowledge/attention](../my_knowledge/attention/) | 未开始 |

周末：按 [复盘模板](../templates/weekly-review.md) 记录独立成果、卡点、到期复习和下周调整。

## 第 3 周：基准与性能分析（2026-11-21 ～ 2026-11-27）

| ID / 计划日期 | 任务 | 验收条件 | 成果位置 | 状态 |
|---|---|---|---|---|
| T08<br>2026-11-21 ～ 2026-11-24 | 可复现的推理基准 | 固定模型/精度/长度/batch/硬件/版本，完成 warmup、重复测量和正确同步。<br>分别报告 Prefill 与 Decode 延迟、输出 token/s 和显存；CPU 结果只作为 CPU 基线。<br>区分 TTFT、TPOT、ITL、端到端延迟和吞吐口径，记录排队/网络是否包含在内。 | [labs/05-performance](../labs/05-performance/) | 未开始 |
| T09<br>2026-11-25 ～ 2026-11-27 | Roofline 与系统性能分析入门 | 用 FLOPs、搬运字节数和硬件能力估算下界，解释 batch、上下文对算术强度的影响。<br>用 torch.profiler，具备 GPU 时用 Nsight Systems 获取时间线，区分 CPU 空洞、kernel、同步和通信。<br>提出一个可检验的瓶颈假设，并用数据说明证据和未验证部分。 | [labs/05-performance](../labs/05-performance/) | 未开始 |

周末：按 [复盘模板](../templates/weekly-review.md) 记录独立成果、卡点、到期复习和下周调整。

## 第 4 周：极简推理引擎（2026-11-28 ～ 2026-12-04）

| ID / 计划日期 | 任务 | 验收条件 | 成果位置 | 状态 |
|---|---|---|---|---|
| T10<br>2026-11-28 ～ 2026-12-01 | nano-vLLM 请求全链路 | 固定所读仓库 URL 与 commit，画出请求、scheduler、KV 分配、model runner 到 attention 的调用图。<br>追踪一个短请求，解释其 prefill/decode 两阶段状态变化；标注实际运行或静态走读。 | [labs/03-engine](../labs/03-engine/) | 未开始 |
| T11<br>2026-12-02 ～ 2026-12-04 | Paged KV、连续批处理与原型 | 实现 CPU block allocator/请求调度原型，覆盖分配、释放、复用和内存不足情况。<br>解释逻辑页/物理块、尾块浪费、连续批处理和 prefix sharing；模拟结果不声称是 GPU 性能收益。 | [labs/03-engine](../labs/03-engine/) | 未开始 |

周末：按 [复盘模板](../templates/weekly-review.md) 记录独立成果、卡点、到期复习和下周调整。

## 第 5 周：生产框架源码（2026-12-05 ～ 2026-12-11）

| ID / 计划日期 | 任务 | 验收条件 | 成果位置 | 状态 |
|---|---|---|---|---|
| T12<br>2026-12-05 ～ 2026-12-08 | vLLM 关键源码走读 | 固定 vLLM commit，定位 API、engine、scheduler、KV manager、worker、attention backend。<br>用实际符号和文件行号建立一条请求调用链；有环境时记录日志，否则明确仅静态分析。<br>解释 token 预算、抢占、chunked prefill 与 KV 生命周期，至少分析一个边界情况。 | [labs/03-engine](../labs/03-engine/) | 未开始 |
| T13<br>2026-12-09 ～ 2026-12-11 | 推理框架小改动与验证 | 实现一个有明确动机的埋点、调度实验或 KV 管理改动，保留 diff 和固定源码版本。<br>验证改动正确性与基线，对比结果并说明统计波动；埋点本身不声称是加速。 | [labs/03-engine](../labs/03-engine/) | 未开始 |

周末：按 [复盘模板](../templates/weekly-review.md) 记录独立成果、卡点、到期复习和下周调整。

## 第 6 周：CUDA 基础与算子（2026-12-12 ～ 2026-12-18）

| ID / 计划日期 | 任务 | 验收条件 | 成果位置 | 状态 |
|---|---|---|---|---|
| T14<br>2026-12-12 ～ 2026-12-14 | CUDA 执行模型、访存与 Reduction | 独立实现向量加和 reduction，理解 grid/block/warp、合并访存、同步和越界处理。<br>在 NVIDIA GPU 上编译运行，覆盖非整齐尺寸，对齐参考结果并记录 CUDA Events 测时。 | [labs/04-cuda](../labs/04-cuda/) | 未开始 |
| T15<br>2026-12-15 ～ 2026-12-18 | CUDA Softmax / RMSNorm 与 Profiling | 独立实现至少一个稳定 Softmax 或 RMSNorm kernel，验证精度与不同形状。<br>使用 Nsight Compute 分析带宽、寄存器、occupancy 等指标，提出并验证一项改动。<br>保留基线、数据和慢于参考的情况，解释 occupancy 不是性能的唯一指标。 | [labs/04-cuda](../labs/04-cuda/) | 未开始 |

周末：按 [复盘模板](../templates/weekly-review.md) 记录独立成果、卡点、到期复习和下周调整。

## 第 7 周：矩阵与 Attention 优化（2026-12-19 ～ 2026-12-25）

| ID / 计划日期 | 任务 | 验收条件 | 成果位置 | 状态 |
|---|---|---|---|---|
| T16<br>2026-12-19 ～ 2026-12-22 | Tiled GEMM 与 Tensor Core 基础 | 实现 shared-memory tiled GEMM，解释 tile 复用、同步和 bank conflict，完成非整齐形状正确性。<br>与 torch/cuBLAS 比较，区分 CUDA Core 与 Tensor Core 路径；理解 CUTLASS/CuTe 的定位。 | [labs/04-cuda](../labs/04-cuda/) | 未开始 |
| T17<br>2026-12-23 ～ 2026-12-25 | FlashAttention 与 PagedAttention 的边界 | 推导 online softmax，解释 tiling 如何避免物化完整 attention scores 及减少 HBM IO。<br>区分 FlashAttention 的计算/IO 优化与 Paged KV 的分配/寻址优化。<br>用小张量实现分块 attention 并对齐参考；高性能 CUDA 完整实现可继续作为扩展。 | [my_knowledge](../my_knowledge/) | 未开始 |

周末：按 [复盘模板](../templates/weekly-review.md) 记录独立成果、卡点、到期复习和下周调整。

## 第 8 周：调度与推理加速（2026-12-26 ～ 2027-01-01）

| ID / 计划日期 | 任务 | 验收条件 | 成果位置 | 状态 |
|---|---|---|---|---|
| T18<br>2026-12-26 ～ 2026-12-29 | 调度、Prefix Cache 与 SGLang 对照 | 固定 SGLang commit，对照调度器、Radix cache、KV pool 与 vLLM 的对应机制。<br>设计长短请求混合、共享前缀等工作负载，对比一个调度/缓存选项对 TTFT、TPOT 和吞吐的影响。<br>真实引擎压测需要 GPU，模拟仅记录机制结论。 | [labs/03-engine](../labs/03-engine/) | 未开始 |
| T19<br>2026-12-30 ～ 2027-01-01 | CUDA Graph 与量化实验 | 解释 CUDA Graph 的启动开销收益与形状/内存限制，测量一个启用/关闭对照。<br>区分权重、激活、KV 量化，分析选定可用格式的显存、延迟与质量变化；不得省略质量验证。 | [labs/05-performance](../labs/05-performance/) | 未开始 |

周末：按 [复盘模板](../templates/weekly-review.md) 记录独立成果、卡点、到期复习和下周调整。

## 第 9 周：分布式与 PD 分离（2027-01-02 ～ 2027-01-08）

| ID / 计划日期 | 任务 | 验收条件 | 成果位置 | 状态 |
|---|---|---|---|---|
| T20<br>2027-01-02 ～ 2027-01-04 | 并行策略、NCCL 与硬件拓扑 | 解释 TP/DP/PP/EP 的切分和通信位置，估算一层 TP 通信量，记录计量口径。<br>解读实际或明确来源的 NVLink/PCIe 拓扑，掌握 AllReduce/AllGather/AlltoAll；真实多卡测量需要设备。 | [my_knowledge](../my_knowledge/) | 未开始 |
| T21<br>2027-01-05 ～ 2027-01-08 | PD 分离与 KV 传输 | 画出 prefill、KV 传输、decode、路由和失败恢复时序，估算 KV 传输下界。<br>实现带请求状态和 KV 生命周期的原型或跑通真实 PD；明确模拟/单机/多机的证据等级。<br>说明 PD 在何种工作负载和互连下可能变慢，分析成本、队列和 SLO 取舍。 | [labs/03-engine](../labs/03-engine/) | 未开始 |

周末：按 [复盘模板](../templates/weekly-review.md) 记录独立成果、卡点、到期复习和下周调整。

## 第 10 周：优化项目实践（2027-01-09 ～ 2027-01-15）

| ID / 计划日期 | 任务 | 验收条件 | 成果位置 | 状态 |
|---|---|---|---|---|
| T22<br>2027-01-09 ～ 2027-01-15 | 优化项目：基线、瓶颈与一次改动 | 选定一个实际可用硬件和固定模型/引擎版本，保存基线配置、测量脚本和原始小型结果。<br>用 profile 锁定一个瓶颈，实施一项可审查的修改，完成正确性与性能对照。<br>无加速也如实记录，并解释原因、局限和下一次实验；缺实测设备时保持待完成。 | [projects/inference-optimization](../projects/inference-optimization/) | 未开始 |

周末：按 [复盘模板](../templates/weekly-review.md) 记录独立成果、卡点、到期复习和下周调整。

## 第 11 周：异构硬件与扩展（2027-01-16 ～ 2027-01-22）

| ID / 计划日期 | 任务 | 验收条件 | 成果位置 | 状态 |
|---|---|---|---|---|
| T23<br>2027-01-16 ～ 2027-01-18 | 昇腾、Ascend C 与 CANN 概念映射 | 基于官方资料解释 AI Core、Cube/Vector、UB、tiling、流水线与 HCCL，映射 CUDA 的相关概念。<br>分析一个官方 Ascend C 样例及内存/同步差异；无 NPU 时只验收理论走读，适配实战仍列为缺口。 | [my_knowledge](../my_knowledge/) | 未开始 |
| T24<br>2027-01-19 ～ 2027-01-22 | 投机解码、MoE/MLA 与 JD 扩展 | 解释 draft/verify、接受率与开销，说明保持目标采样分布需要满足的算法条件。<br>说明 MoE 的专家通信、MLA 对 KV 的影响；了解多模态 token 和内存变化，不伪造实战经历。<br>形成 TensorRT-LLM/CANN/DSpark 后续清单，DSpark 的具体实现与版本需向岗位方核实。 | [my_knowledge](../my_knowledge/) | 未开始 |

周末：按 [复盘模板](../templates/weekly-review.md) 记录独立成果、卡点、到期复习和下周调整。

## 第 12 周：复现与面试验收（2027-01-23 ～ 2027-01-29）

| ID / 计划日期 | 任务 | 验收条件 | 成果位置 | 状态 |
|---|---|---|---|---|
| T25<br>2027-01-23 ～ 2027-01-26 | 优化项目整理与复现 | 提供环境、命令、配置、正确性结果、性能统计、profile 证据和改动说明，使他人能复现。<br>写清单卡/多卡边界、失败案例与业务影响，形成真实可讲述的项目材料。 | [projects/inference-optimization](../projects/inference-optimization/) | 未开始 |
| T26<br>2027-01-27 ～ 2027-01-29 | 限时面试与能力盘点 | 不看资料完成 Attention/KV/FLOPs 推导题、源码链路题、CUDA 分析题和 PD 设计题。<br>用 20 分钟讲清项目问题、证据、改动、验证与局限，保留回答和反馈。<br>逐项对照 JD 标注已验证/仅理论/待补，不把 12 周学习等同于 3 年开发经历。 | [learning/reviews](../learning/reviews/) | 未开始 |

周末：按 [复盘模板](../templates/weekly-review.md) 记录独立成果、卡点、到期复习和下周调整。

## 阶段验收

- 第 2 周：独立完成带 KV Cache 的小型 Decoder，推导形状、FLOPs 与显存。
- 第 5 周：解释真实推理引擎请求链路，完成一项可验证的小改动。
- 第 8 周：具备 CUDA 基础、算子实测和调度/加速实验的证据。
- 第 12 周：完成可复现项目与限时问答，并明确仍缺的多卡／昇腾／生产经验。

没有设备、验收未通过或投入时间不足时顺延。TensorRT-LLM 深入开发、真实 Ascend C 适配、大规模集群实践为后续专项，不能用理论阅读替代。
