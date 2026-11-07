# 小型 Decoder 实验

对应 T06、T07。依次实现 RMSNorm、RoPE、SwiGLU、残差连接和多层 Decoder，使用随机权重即可。保存环境、形状、全序列与缓存推理对齐命令、最大误差和边界用例。

成本分析分别列出权重、KV、临时张量，声明 batch、长度、精度、GQA heads、乘加口径；用实际 `numel()` 交叉验证。CPU 可做正确性，GPU 显存和性能结论必须来自实测。
