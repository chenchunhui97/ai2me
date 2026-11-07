# 第一站：从 Attention 形状到 KV Cache

对应 T01～T05。第一项 **T01** 先完成下面的诊断，避免跳过当前最需要练的形状与计算。初始文件只提供任务，不提供完成答案或把示例标记为学习成果。

## 第一次学习，45～60 分钟

1. 运行 `python3 scripts/study.py start T01`。
2. 不看答案，花 15 分钟写出下面三道题的回答，保存到 `my_knowledge/attention/shapes.md`。
3. 用 20～30 分钟编写小张量验证脚本，使用自己当前可用的 PyTorch 环境，CPU 即可；不要创建完整 `[16,1024,1024]` scores 作为第一步。
4. 请助手检查，写明错误与得到的提示，保存 session，记录 `attempt` 或满足验收后的 `pass`。

## T01 诊断题

设 `B=1,S=1024,H=2048,Qheads=16,KVheads=4,d=128`。

1. 使用 `X @ W` 的权重约定，写出 X、Wq/Wk/Wv/Wo、投影后及拆头后的 Q/K/V、逻辑 scores、合头后输出的形状。每一步说明输入维度如何对应。PyTorch `nn.Linear` 的权重存储布局与这个约定有什么关系？
2. Query heads 是 KV heads 的 4 倍，具体如何配对？直接把 Q 与原始 K 做矩阵乘法会遇到什么形状问题？写出正确的逻辑分组方案。
3. 把 B 改为 2、S 改为 17，其余不变，再推导一次。用 `B=2,S=5,H=32,Qheads=4,KVheads=2,d=8` 的随机小张量检查程序形状；标注程序做了哪些显式复制。

记录格式：题目、原始答案、实际代码、运行命令与输出、错误与修正、辅助程度。卡住时直接告诉助手你卡在哪一步。

## T02～T05 的实现顺序

- T02：稳定 Softmax、单头 Attention、causal mask。无未来信息泄漏，和参考输出对齐。
- T03：MHA、投影与 split/merge heads。理解 reshape、transpose、contiguous。
- T04：GQA/MQA，独立说明 head 映射和 KV 存储变化。
- T05：Prefill、KV 追加、逐 token Decode，对齐全序列重算；特别检查非零 past length 的位置和 mask。

可以用 `torch.nn.functional.scaled_dot_product_attention` 作为验证参考；自写主实现仍使用基础张量运算。存在 past KV 时，需明确构造正确的位置和 mask，不盲目依赖非方形输入的 `is_causal=True` 行为。先对齐 FP32 数值，再讨论低精度误差。

实际验收条件以 `python3 scripts/study.py show T01` 等命令为准。每阶段只提交自己完成的代码和真实输出，不把助手直接给出的完整答案当作独立完成。
