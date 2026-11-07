# 基准与性能分析

对应 T08、T09、T19，后续为项目提供测量工具。先固定 workload 和统计口径，区分 TTFT、TPOT、ITL、整体吞吐与每请求速度。定义 TPOT 时说明是否排除首 token 及少于两个输出 token 的处理方式。

使用 [实验模板](../../templates/experiment.md)，保存可运行命令、配置、少量 CSV/JSON 结果及结论。计时需考虑 GPU 异步、warmup、编译/图捕获和并发；profile 的开销不能直接当作正常吞吐。性能改进需要相同条件的基线和正确性验证。
