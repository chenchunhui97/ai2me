# GitHub 多电脑同步

GitHub 保存整个学习助手，以及个人学习日志、总结、进度、练习代码和小型实验结果。只在本机保存但未 commit、未 push 的内容，另一台电脑无法取得。`scripts/study.py` 负责记档与生成面板，不自动调用 Git 或上传。

## 同步范围

| 路径 | 是否同步 |
|---|---|
| `learning/` | 是，包括 profile、课程、事件日志、时间线、进度、session、复盘 |
| `my_knowledge/` | 是，包括个人推导、知识总结、错误修正 |
| `labs/`、`projects/` | 是，包括代码、配置、小型测量结果 |
| `papers/` 下的 Markdown | 是，包括论文阅读总结 |
| `target/`、`templates/`、`tutor/`、`AGENTS.md` | 是，换电脑后可恢复协作方式 |
| 独立参考仓库、PDF、模型、数据、大型 profile、本机配置 | 按 `.gitignore` 本机保留 |

参考仓库的来源与版本由 `learning/references.json` 同步，另一个电脑按 [资料索引](RESOURCES.md) 重建即可。学习助手的状态查询不需要先下载这些资料。

## 新电脑第一次使用

远端仓库：https://github.com/chenchunhui97/ai2me 。先配置该电脑访问 GitHub 的 SSH Key 或 HTTPS 凭据，再克隆：

```bash
git clone https://github.com/chenchunhui97/ai2me.git my-learn
cd my-learn
python3 scripts/study.py check
python3 scripts/study.py status
python3 scripts/study.py next
```

在编辑器打开目录，对助手说“读取仓库进度，继续学习”。脚本使用 Python 3.9+；Linux/macOS 原生支持所用文件锁，Windows 可在 WSL 中运行。

## 每次开始学习

先确认上一台电脑已经提交并推送，当前工作区没有未保存的修改：

```bash
git status
git pull --ff-only
python3 scripts/study.py check
python3 scripts/study.py next
```

若有未提交成果，先保存为本地提交；不要通过丢弃修改来完成 pull。`--ff-only` 遇到本地和远端分别有新提交时会停止，需要先审查并合并，不能覆盖任一侧成果。

## 学习结束并同步

让助手执行：“今天收工，保存学习日志、总结和进度，并推送到 GitHub。”也可以手动执行：

```bash
python3 scripts/study.py check
git status
git add learning my_knowledge labs projects papers
git diff --cached
git commit -m "study: 记录本次学习成果与进度"
git push
```

没有新改动时跳过 commit；文档、工具等额外改动按需要明确加入暂存区。首次推送需设置分支上游：`git push -u origin main`，后续使用 `git push`。

以命令实际成功且远端分支包含本地提交为同步完成；未 push 的本地 commit 不能当作另一台电脑已可拉取。

## 两台电脑都有未同步的提交

先 `git fetch origin`，检查分支和改动后，通常使用 `git merge origin/main` 保留两边提交。冲突解决时：

1. `learning/events.jsonl` 保留两边真实事件，维持各自事件内部顺序，不删除、复制或伪造事件。若新顺序不满足前置验收依赖，需要结合实际学习先后人工排查。
2. session、笔记和代码逐项合并，保留两边成果。
3. 时间线和进度是生成视图，解决来源文件冲突后运行 `python3 scripts/study.py render` 重建。
4. 执行 `python3 scripts/study.py check`，检查 diff，完成合并提交，再 `git push`。

遇到不确定的进度事件冲突请让助手检查。正常同步不使用 force push，也不 reset 丢弃未同步成果。
