#!/usr/bin/env python3
"""Offline learning tracker. Curriculum + append-only events -> Markdown views."""

import argparse
from contextlib import contextmanager
from datetime import date, datetime, timedelta
import fcntl
import json
import os
from pathlib import Path
import tempfile
import uuid
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
STATES = {
    "not_started": "未开始", "learning": "学习中", "passed": "验收通过",
    "blocked": "阻塞", "needs_work": "待巩固",
}
KINDS = {"start", "note", "attempt", "pass", "block", "review-pass", "review-fail", "correction"}
INTERVALS = [1, 3, 7, 14, 30]


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


@contextmanager
def lock(root):
    with (root / "learning/.lock").open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def load(root):
    profile = json.loads((root / "learning/profile.json").read_text(encoding="utf-8"))
    curriculum = json.loads((root / "learning/curriculum.json").read_text(encoding="utf-8"))
    date.fromisoformat(profile["plan_start"])
    ZoneInfo(profile["timezone"])
    if profile.get("schema_version") != 1 or curriculum.get("schema_version") != 1:
        raise ValueError("不支持的数据版本")
    tasks = curriculum["tasks"]
    ids = [t["id"] for t in tasks]
    if len(ids) != len(set(ids)) or not ids:
        raise ValueError("任务 ID 重复或课程为空")
    seen = set()
    for task in tasks:
        if not set(task["depends_on"]) <= seen:
            raise ValueError(f'{task["id"]}: 依赖必须存在并排在当前任务之前')
        if not 0 <= task["start_day"] <= task["end_day"]:
            raise ValueError("任务日期范围不合法")
        if not task["acceptance"] or not (root / task["artifact_dir"]).is_dir():
            raise ValueError(f'{task["id"]}: 缺验收条件或成果目录')
        seen.add(task["id"])
    events = []
    for number, line in enumerate((root / "learning/events.jsonl").read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise ValueError(f"events.jsonl 第 {number} 行为空")
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"events.jsonl 第 {number} 行损坏: {exc}") from exc
    return profile, curriculum, events


def evidence_path(root, name):
    if not isinstance(name, str) or not name.strip() or Path(name).is_absolute():
        raise ValueError("证据必须使用非空的仓库相对文件路径")
    target = (root / name).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError(f"证据文件不存在或超出仓库: {name}")
    if any(part.startswith(".") for part in Path(name).parts) or ".." in Path(name).parts:
        raise ValueError("证据不能放在隐藏目录或使用父目录路径")
    if Path(name).parts[0] in {"AI-System", "AI-fundamentals", "aik8s", "InfraTech", "papers"}:
        raise ValueError("请引用个人成果文件，不能用忽略的参考资料充当证据")
    if not target.stat().st_size:
        raise ValueError(f"证据文件为空: {name}")
    return target


def replay(root, tasks, events):
    lookup = {t["id"]: t for t in tasks}
    state = {t["id"]: {"status": "not_started", "minutes": 0, "due": None,
                          "review_index": 0, "ever_passed": False, "last": None} for t in tasks}
    event_ids = set()
    for event in events:
        ident, kind = event["task"], event["kind"]
        if ident not in state or kind not in KINDS:
            raise ValueError("未知任务或事件类型")
        if not isinstance(event["id"], str) or not event["id"] or event["id"] in event_ids:
            raise ValueError("事件 ID 为空或重复")
        event_ids.add(event["id"])
        timestamp = datetime.fromisoformat(event["at"])
        if timestamp.utcoffset() != timedelta(hours=8):
            raise ValueError("事件时间必须显式使用上海时区 +08:00")
        minutes = event["minutes"]
        if type(minutes) is not int or minutes < 0:
            raise ValueError("学习分钟必须为非负整数")
        if not isinstance(event["summary"], str) or not event["summary"].strip():
            raise ValueError("事件必须有真实摘要")
        evidence = event.get("evidence", [])
        if not isinstance(evidence, list):
            raise ValueError("evidence 必须为文件列表")
        for name in evidence:
            evidence_path(root, name)
        item = state[ident]
        if kind == "correction" and event.get("state") not in STATES:
            raise ValueError("更正必须指定合法 --state")
        passing = kind in {"pass", "review-pass"} or (kind == "correction" and event["state"] == "passed")
        if passing:
            if event.get("independent") is not True or not evidence:
                raise ValueError("验收通过需 --independent 与至少一个非空证据文件")
            missing = [d for d in lookup[ident]["depends_on"] if state[d]["status"] != "passed"]
            if missing:
                raise ValueError(f"前置任务尚未通过: {', '.join(missing)}")
        if kind in {"review-pass", "review-fail"} and not item["ever_passed"]:
            raise ValueError("尚未初次通过任务，不能记录复习，请用 attempt/pass")
        if kind == "pass" and item["status"] == "passed":
            raise ValueError("任务已通过，复习请使用 review-pass")
        if kind == "start":
            missing = [d for d in lookup[ident]["depends_on"] if state[d]["status"] != "passed"]
            if missing:
                raise ValueError(f"先完成前置任务: {', '.join(missing)}")
        item["minutes"] += minutes
        item["last"] = event
        if kind == "start":
            item["status"] = "learning"
        elif kind == "attempt":
            if item["status"] != "passed":
                item["status"] = "learning"
        elif kind == "block":
            item["status"] = "blocked"
        elif passing:
            item["status"] = "passed"
            item["ever_passed"] = True
            item["review_index"] = min(item["review_index"] + 1, len(INTERVALS) - 1) if kind == "review-pass" else 0
            item["due"] = (timestamp.date() + timedelta(days=INTERVALS[item["review_index"]])).isoformat()
        elif kind == "review-fail":
            item["status"] = "needs_work"
            item["review_index"] = -1
            item["due"] = (timestamp.date() + timedelta(days=1)).isoformat()
        elif kind == "correction":
            item["status"] = event["state"]
            item["due"] = None
            item["ever_passed"] = False
            item["review_index"] = 0
    return state


def recommendations(tasks, state, today):
    due = [t for t in tasks if state[t["id"]]["due"] and
           state[t["id"]]["due"] <= today.isoformat() and
           state[t["id"]]["status"] in {"passed", "needs_work"} and
           all(state[d]["status"] == "passed" for d in t["depends_on"])]
    ongoing = [t for t in tasks if state[t["id"]]["status"] in {"learning", "needs_work"} and
               all(state[d]["status"] == "passed" for d in t["depends_on"])]
    fresh = [t for t in tasks if state[t["id"]]["status"] == "not_started" and
             all(state[d]["status"] == "passed" for d in t["depends_on"])]
    return due, ongoing, fresh


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def views(profile, curriculum, events, state):
    start = date.fromisoformat(profile["plan_start"])
    tasks = curriculum["tasks"]
    passed = sum(v["status"] == "passed" for v in state.values())
    timeline = ["# 学习时间线", "", "由 `learning/curriculum.json`、`profile.json` 和学习事件生成；修改计划后运行 `python3 scripts/study.py render`。", "",
                f"起始日期：**{start}**；预算：每周 **{'～'.join(map(str, profile['weekly_hours']))} 小时**（尚待确认）。日期是建议，完成状态以真实验收为准。", "",
                "前两周优先完成可独立实现、可计算、可验证的模型基础。每次安排约 10 分钟回忆、15～25 分钟理解、30～60 分钟独立实践和 10 分钟记录；按实际时间拆分。", ""]
    for week in curriculum["weeks"]:
        begin = start + timedelta(days=(week["week"] - 1) * 7)
        timeline += [f"## 第 {week['week']} 周：{week['title']}（{begin} ～ {begin + timedelta(days=6)}）", "",
                     "| ID / 计划日期 | 任务 | 验收条件 | 成果位置 | 状态 |", "|---|---|---|---|---|"]
        for task in [t for t in tasks if t["week"] == week["week"]]:
            begin, end = (start + timedelta(days=task[k]) for k in ("start_day", "end_day"))
            acceptance = "<br>".join(cell(a) for a in task["acceptance"])
            path = task["artifact_dir"]
            timeline.append(f"| {task['id']}<br>{begin} ～ {end} | {task['title']} | {acceptance} | [{path}](../{path}/) | {STATES[state[task['id']]['status']]} |")
        timeline += ["", "周末：按 [复盘模板](../templates/weekly-review.md) 记录独立成果、卡点、到期复习和下周调整。", ""]
    timeline += ["## 阶段验收", "", "- 第 2 周：独立完成带 KV Cache 的小型 Decoder，推导形状、FLOPs 与显存。", "- 第 5 周：解释真实推理引擎请求链路，完成一项可验证的小改动。", "- 第 8 周：具备 CUDA 基础、算子实测和调度/加速实验的证据。", "- 第 12 周：完成可复现项目与限时问答，并明确仍缺的多卡／昇腾／生产经验。", "", "没有设备、验收未通过或投入时间不足时顺延。TensorRT-LLM 深入开发、真实 Ascend C 适配、大规模集群实践为后续专项，不能用理论阅读替代。", ""]
    progress = ["# 学习进度", "", "由原始事件重建；没有学习证据的任务保持未开始。实时复习推荐运行 `python3 scripts/study.py next`。", "",
                f"- 当前验收通过：**{passed}/{len(tasks)}**（仅任务计数，不是岗位匹配率）", f"- 已记录学习时间：**{sum(v['minutes'] for v in state.values())} 分钟**", f"- 学习事件：**{len(events)} 条**", "- 当前背景与待确认条件：[profile.json](profile.json)", "",
                "| ID | 任务 | 当前状态 | 学习分钟 | 下次复习 | 最近记录 |", "|---|---|---|---|---|---|"]
    for task in tasks:
        item = state[task["id"]]
        last = item["last"]
        summary = f"{last['at'][:10]}：{cell(last['summary'])}" if last else "尚无实际练习证据"
        progress.append(f"| {task['id']} | {task['title']} | {STATES[item['status']]} | {item['minutes']} | {item['due'] or '—'} | {summary} |")
    progress += ["", "## 使用入口", "", "1. `python3 scripts/study.py next` 选定下一项。", "2. `show ID` 查看验收，再 `start ID`。", "3. 保存 session、代码／推导／实验结果，用 `record` 记录真实完成情况。", "4. `check` 检查一致性，Git 保存本次学习成果。", "", "初始建仓记录见 [2026-11-07-onboarding.md](sessions/2026-11-07-onboarding.md)，它不计为学习验收。", ""]
    return {"learning/TIMELINE.md": "\n".join(timeline), "learning/PROGRESS.md": "\n".join(progress)}


def render(root, profile, curriculum, events, state):
    for name, content in views(profile, curriculum, events, state).items():
        atomic_write(root / name, content)


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    for command in ("status", "next", "render", "check"):
        commands.add_parser(command)
    for command in ("show", "start", "record"):
        child = commands.add_parser(command)
        child.add_argument("task")
        if command == "record":
            child.add_argument("--kind", choices=sorted(KINDS - {"start"}), required=True)
            child.add_argument("--summary", required=True)
            child.add_argument("--minutes", type=int, default=0)
            child.add_argument("--evidence", action="append", default=[])
            child.add_argument("--independent", action="store_true")
            child.add_argument("--state", choices=sorted(STATES))
    child = commands.add_parser("reschedule")
    child.add_argument("--start", required=True, type=date.fromisoformat)
    return result


def main(argv=None, root=ROOT):
    args = parser().parse_args(argv)
    try:
        with lock(root):
            profile, curriculum, events = load(root)
            tasks = curriculum["tasks"]
            state = replay(root, tasks, events)
            now = datetime.now(ZoneInfo(profile["timezone"]))
            if args.command in {"start", "record", "show"}:
                task = next((t for t in tasks if t["id"] == args.task), None)
                if task is None:
                    raise ValueError(f"未知任务: {args.task}")
            if args.command == "show":
                print(f"{task['id']} {task['title']}\n前置任务：{', '.join(task['depends_on']) or '无'}\n成果目录：{task['artifact_dir']}")
                for index, criterion in enumerate(task["acceptance"], 1):
                    print(f"{index}. {criterion}")
            elif args.command in {"start", "record"}:
                event = {"id": uuid.uuid4().hex, "at": now.isoformat(timespec="seconds"),
                         "task": args.task, "kind": "start" if args.command == "start" else args.kind,
                         "summary": f"开始 {task['title']}" if args.command == "start" else args.summary,
                         "minutes": getattr(args, "minutes", 0), "evidence": getattr(args, "evidence", []),
                         "independent": getattr(args, "independent", False)}
                if getattr(args, "state", None):
                    event["state"] = args.state
                updated = events + [event]
                state = replay(root, tasks, updated)
                # Preserve the complete original byte prefix when adding a new event.
                path = root / "learning/events.jsonl"
                original = path.read_text(encoding="utf-8")
                separator = "\n" if original and not original.endswith("\n") else ""
                atomic_write(path, original + separator + json.dumps(event, ensure_ascii=False) + "\n")
                render(root, profile, curriculum, updated, state)
                print(f"已记录 {event['kind']}：{args.task}，当前状态 {STATES[state[args.task]['status']]}")
            elif args.command == "reschedule":
                profile["plan_start"] = args.start.isoformat()
                atomic_write(root / "learning/profile.json", json.dumps(profile, ensure_ascii=False, indent=2) + "\n")
                render(root, profile, curriculum, events, state)
                print(f"计划起始日期调整为 {args.start}，实际学习事件保持原样。")
            elif args.command == "render":
                render(root, profile, curriculum, events, state)
                print("已生成学习时间线与进度。")
            elif args.command == "check":
                for name, content in views(profile, curriculum, events, state).items():
                    if not (root / name).is_file() or (root / name).read_text(encoding="utf-8") != content:
                        raise ValueError(f"生成视图过期或缺失: {name}；请运行 render")
                print(f"检查通过：{len(tasks)} 个任务、{len(events)} 个事件，依赖、证据和生成视图一致。")
            else:
                due, ongoing, fresh = recommendations(tasks, state, now.date())
                if args.command == "status":
                    print(f"验收通过 {sum(v['status'] == 'passed' for v in state.values())}/{len(tasks)}；记录学习 {sum(v['minutes'] for v in state.values())} 分钟；到期复习 {len(due)} 项。")
                choices = [("到期复习", due), ("继续学习", ongoing), ("下一项", fresh)]
                for label, items in choices:
                    if items:
                        task = items[0]
                        print(f"{label}：{task['id']} {task['title']}（show {task['id']} 查看验收）")
                        if args.command == "next":
                            break
                for task in tasks:
                    item = state[task["id"]]
                    if item["status"] == "blocked":
                        print(f"阻塞：{task['id']} {item['last']['summary']}")
                if not any((due, ongoing, fresh)):
                    print("暂无可自动推荐的新任务，请检查阻塞和进度；已通过内容按期复习。")
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"错误：{exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
