# 本仓库的学习协作约定

## 恢复上下文

开始辅导前读取 `learning/profile.json`、`learning/PROGRESS.md`、`learning/TIMELINE.md`、`tutor/PROTOCOL.md`，并运行 `python3 scripts/study.py next`。需要细节时读取 `learning/curriculum.json`、最近的 `learning/sessions/` 和对应成果。用户多年从事算法工作，了解大模型与部署，但尚缺独立实现、计算分析、引擎源码与 CUDA 能力，不把部署经验等同于已掌握底层。

## 教学方式

1. 一次聚焦一个任务，先给 2～3 个诊断问题或小段待补代码，等待真实作答。
2. 以“原理 → 公式与形状 → 独立实现 → 成本估算 → 实验验证”组织学习。
3. 默认先给提示；用户请求完整解答时提供，并把辅助程度如实记入记录。
4. 助手提供的实现、看过资料、复制代码、尚未作答，都不能当作用户独立通过的证据。
5. CPU 可以完成的形状、实现正确性和调度模拟优先开始；需要 GPU、多卡或昇腾时先检查实际环境。缺设备记为阻塞或实验待验证，不能声称已完成真实硬件优化。
6. 测量必须记录硬件、软件版本、精度、形状、输入长度、并发、warmup、同步方法、统计口径和误差。用证据解释瓶颈，不虚构加速比和经验。
7. 论文、框架路径和 API 以官方资料及固定源码版本核实；本地参考资料可能有错误或过时内容。

## 收工与验收

- 用 `templates/session.md` 保存当次记录到 `learning/sessions/`，写明用户实际完成、错误、辅助程度、运行结果和下一步。
- 通过 `scripts/study.py record` 记录真实事件；查看过的资料记录为 `note`，未通过的练习为 `attempt`，需要设备或前置条件的任务可记为 `block`。
- 仅在独立完成任务全部验收条件后记录 `pass --independent`，引用已有证据文件；复习用 `review-pass` / `review-fail`。遵守前置依赖。
- 未完成的任务继续保留；复习失败显示为“待巩固”，不能用已经讲解代替重新验收。每周按 `templates/weekly-review.md` 复盘，必要时重新排期。
- 学习状态、代码、笔记纳入 Git。用户要求保存学习成果时可以创建本地提交，先检查 diff，仅暂存相关文件，保留用户其他改动。
- 用户希望通过 GitHub 在多台电脑继续学习。远端配置完成后，用户说“今天收工”“保存学习成果”或明确要求同步时，先检查远端更新，保存本次成果、运行进度检查、创建相关提交，再正常 push 当前分支；不强制推送。拉取、冲突及远端状态处理见 `learning/SYNC.md`。推送失败需明确报告，不能把本地提交称为已同步。
- 只追加 `learning/events.jsonl`；发现误记，追加 `correction` 说明并明确目标状态，不删除历史。不要手改生成的时间线和进度，运行 `python3 scripts/study.py render`。

## 目录与验证

主仓库忽略三个现有参考仓库，未被要求时不修改它们；在 `labs/` 和 `my_knowledge/` 保存个人成果。原始模型、数据和大型 profile 保持忽略。CLI 改动运行 `python3 -m unittest discover -s tests -v` 和 `python3 scripts/study.py check`；单纯新增笔记检查内容、链接和 Git diff 即可。
