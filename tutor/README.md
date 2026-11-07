# 学习助手使用

自然语言入口和目录说明见根目录 [README](../README.md)。助手根据 [协议](PROTOCOL.md) 读取状态，不依赖上一轮聊天记忆；数据工具使用 Python 3.9+ 标准库，文件锁使用 Linux/macOS 的 `fcntl`。

```bash
python3 scripts/study.py status
python3 scripts/study.py next
python3 scripts/study.py show T01
python3 scripts/study.py start T01
```

每次结束，先保存一份 session 和实际成果，再记录事件：

```bash
# 提交前替换为真实的内容和文件；示例文件不作为已完成证据。
python3 scripts/study.py record T01 --kind attempt --minutes 30 \
  --summary '独立写完形状表，仍需检查 mask 广播' \
  --evidence learning/sessions/2026-11-07-t01.md

# 缺 GPU 等问题用 block，原因写在 summary；恢复时重新 start。
python3 scripts/study.py record T14 --kind block \
  --summary '尚无可用 NVIDIA GPU，CUDA 实测待安排'

# 复习通过与初次通过同样要求独立作答、已有证据。
python3 scripts/study.py record T01 --kind review-pass --independent \
  --summary '独立完成 GQA 变式，形状与占用计算均正确' \
  --evidence learning/sessions/2026-11-08-t01-review.md

# 复习未通过不会计为掌握。
python3 scripts/study.py record T01 --kind review-fail \
  --summary '将 KV heads 错写为 Query heads，需要重新练习'

# 更正误记，需真实原因；不删除原事件。
python3 scripts/study.py record T01 --kind correction --state learning \
  --summary '上次只有助手讲解，不能计为独立验收'

python3 scripts/study.py reschedule --start 2026-11-09
python3 scripts/study.py render
python3 scripts/study.py check
```

`status` 显示当前验收通过数、记录分钟数、到期复习和阻塞；不把时长当作掌握度。`next` 根据依赖选择任务，不能证明你已具备对应岗位经验。每周从模板创建复盘，记录计划偏差，按真实能力调整课程。

本版本提供仓库内的自然语言协作规范、离线 CLI 和 Markdown 面板；不需要 API Key，也没有后台自动授课进程。只运行 `status` 或 `next` 不会更改学习进度。
