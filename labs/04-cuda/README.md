# CUDA 算子实验

对应 T14～T17。执行模型与访存 → reduction → Softmax/RMSNorm → tiled GEMM → Attention IO 分析。每个实现先验证数值和边界，再测时，再做 profile。

需要实际 NVIDIA GPU；环境未知时记录阻塞。保存 GPU 型号、compute capability、驱动、CUDA、编译命令、形状/精度、误差、warmup、同步和重复测量统计。大型 Nsight 原始文件放在 `raw_profiles/`，提交小型导出指标和 [实验报告](../../templates/experiment.md)。
