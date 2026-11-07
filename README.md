# 大模型推理性能优化学习助手

面向 `target/` 中的推理优化工程师 JD，记录学习时间线、独立练习、计算推导、源码走读和性能实验。当前背景：多年算法工作经验，了解大模型和推理，但独立实现、计算分析、框架源码和 CUDA 需要补齐。

**从这里开始：[学习时间线](learning/TIMELINE.md) · [当前进度](learning/PROGRESS.md) · [第一项练习](labs/01-attention/README.md)**

## 和助手一起学

以后在这个目录打开 AI 助手，直接说：

- **今天学什么？** 恢复进度，给出一项可在当前时间内完成的练习。
- **开始学习 T01。** 先诊断，再讲解，再让你独立完成。
- **我做完了，帮我验收。** 检查代码、推导和实际运行结果，记录证据。
- **这个地方我不会。** 记录具体错误，安排变式练习。
- **今天收工。** 沉淀本次成果、卡点和下一步。
- **看看进度／复习到期内容。** 展示已完成、未完成、阻塞项和复习任务。

助手的工作约定在 [AGENTS.md](AGENTS.md)，验收与记录规则在 [进度协议](tutor/PROTOCOL.md)。本仓库直接保存学习成果并纳入 Git；原始模型、个人敏感材料和大型 profile 文件放入忽略目录。

## 时间安排

暂按 **2026-11-07 开始、12 周、每周 10～15 小时**排期，这是待确认的时间预算，并非已投入时间或面试准备完成保证。前两周优先打通 Attention → KV Cache → 小型 Decoder → 计算与显存分析。未通过前置任务验收时，顺延后续任务。

```bash
python3 scripts/study.py status        # 当前状态，不需要 GPU 或第三方包
python3 scripts/study.py next          # 到期复习、进行中和下一项可做任务
python3 scripts/study.py show T01      # 任务要求、验收条件、成果位置
python3 scripts/study.py start T01     # 真正开始学习时再执行
python3 scripts/study.py check         # 检查数据、依赖、证据及生成文档
```

记录一次练习（执行前替换成自己的真实结果与已有证据文件）：

```bash
python3 scripts/study.py record T01 --kind attempt --minutes 30 \
  --summary '写出了 Q/K/V 形状，GQA 的 head 映射仍有错误' \
  --evidence my_knowledge/attention/shapes.md

# 满足全部验收条件、独立完成后再记录 pass；助手写好的答案不能充当独立证据。
python3 scripts/study.py record T01 --kind pass --independent --minutes 15 \
  --summary '独立完成全部形状题和不同输入尺寸的变式，见验收记录' \
  --evidence my_knowledge/attention/shapes.md
```

常用命令、复习和调整日期见 [助手使用说明](tutor/README.md)。CLI 只校验记录格式、前置依赖和文件存在性，内容是否正确由你与助手根据验收条件判断。

## 成果放在哪里

| 路径 | 内容 |
|---|---|
| `learning/` | 个人背景、课程、原始学习事件、自动生成的时间线和进度 |
| `learning/sessions/`、`learning/reviews/` | 每次学习记录与每周复盘 |
| `my_knowledge/` | 自己能解释的推导、知识卡、错误与修正 |
| `labs/` | 自己写的模型、引擎原型、CUDA 和 benchmark |
| `projects/inference-optimization/` | 最终优化项目，配置、测量、改动和边界 |
| `templates/` | 学习记录、源码分析、实验和复盘模板 |
| `target/` | 原始岗位截图与需求拆解 |
| `papers/` | 论文阅读索引，原始 PDF 本地保留 |

`learning/curriculum.json` 定义计划，`learning/events.jsonl` 只追加真实学习事件；时间线与进度由脚本生成，避免多份清单不一致。初始学习验收进度为 **0/26**，现有工作经验和资料收藏不自动折算成完成任务。

## Git 记录

```bash
git status
git add learning my_knowledge labs projects
git diff --cached
git commit -m "study(T01): 记录 Attention 形状推导与验收"
```

每次学习结束提交一次有意义的成果；工具可以更新学习记录，提交只包含本次学习相关文件。当前是本地 Git 项目，远端托管地址尚未配置。

已有的 `AI-System/`、`AI-fundamentals/`、`aik8s/` 作为独立参考仓库保留，主仓库不重复纳入其文件和历史；来源及当前提交记录在 [references.json](learning/references.json)，重建方法见 [资料索引](learning/RESOURCES.md)。

新增的 `InfraTech/` 同样作为独立参考目录忽略；建档时该仓库尚无可读取的 HEAD，版本待克隆完成后补录。

## 参考设计

参考 [senior-software-architect-review](https://github.com/PeterGuy326/senior-software-architect-review) 的“诊断 → 练习 → 证据 → 错因 → 间隔复习”组织方式，查阅版本 `67e88104538ca56fd419bc19d4c68f20d97af193`。这里的课程、工具和模板围绕推理优化重新编写；个人学习记录按本仓库目标纳入版本管理。

验证工具：`python3 -m unittest discover -s tests -v`。
