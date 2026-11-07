"""Exercise actual persistence, prerequisites, review transitions and recovery."""

from contextlib import redirect_stdout
from datetime import date
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location("study", Path(__file__).resolve().parents[1] / "scripts/study.py")
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


class StudyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "learning").mkdir()
        (self.root / "labs").mkdir()
        (self.root / "labs/result.md").write_text("独立推导、运行命令与实际输出。", encoding="utf-8")
        profile = {"schema_version": 1, "plan_start": "2026-11-07", "timezone": "Asia/Shanghai", "weekly_hours": [10, 15]}
        curriculum = {"schema_version": 1, "weeks": [{"week": 1, "title": "基础"}], "tasks": [
            {"id": "T01", "week": 1, "title": "第一项", "start_day": 0, "end_day": 1,
             "depends_on": [], "artifact_dir": "labs", "acceptance": ["独立推导"]},
            {"id": "T02", "week": 1, "title": "第二项", "start_day": 2, "end_day": 3,
             "depends_on": ["T01"], "artifact_dir": "labs", "acceptance": ["独立实现"]},
        ]}
        for name, data in (("profile", profile), ("curriculum", curriculum)):
            (self.root / f"learning/{name}.json").write_text(json.dumps(data), encoding="utf-8")
        (self.root / "learning/events.jsonl").touch()

    def invoke(self, *args):
        output = io.StringIO()
        with redirect_stdout(output):
            code = study.main(list(args), root=self.root)
        return code, output.getvalue()

    def state(self):
        _, curriculum, events = study.load(self.root)
        return study.replay(self.root, curriculum["tasks"], events)

    def record(self, kind="pass", task="T01", **kwargs):
        args = ["record", task, "--kind", kind, "--summary", "真实结果摘要"]
        if kind in {"pass", "review-pass"}:
            args += ["--independent", "--evidence", "labs/result.md"]
        for key, value in kwargs.items():
            args += ["--" + key.replace("_", "-"), str(value)]
        return self.invoke(*args)

    def test_fresh_workspace_and_read_commands_do_not_create_learning_events(self):
        self.assertEqual(self.invoke("render")[0], 0)
        self.assertEqual(self.invoke("check")[0], 0)
        self.assertIn("T01", self.invoke("next")[1])
        self.assertIn("0/2", self.invoke("status")[1])
        self.assertEqual((self.root / "learning/events.jsonl").read_text(), "")

    def test_start_and_pass_respect_prerequisites_and_preserve_log_prefix(self):
        self.assertEqual(self.invoke("start", "T02")[0], 1)
        self.assertEqual(self.record(task="T02")[0], 1)
        self.assertEqual(self.invoke("start", "T01")[0], 0)
        before = (self.root / "learning/events.jsonl").read_bytes()
        self.assertEqual(self.record(minutes=30)[0], 0)
        self.assertTrue((self.root / "learning/events.jsonl").read_bytes().startswith(before))
        self.assertEqual(self.state()["T01"]["minutes"], 30)
        self.assertEqual(self.invoke("start", "T02")[0], 0)
        self.assertEqual(self.invoke("check")[0], 0)

    def test_pass_requires_independence_and_nonempty_evidence_without_mutation(self):
        before = (self.root / "learning/events.jsonl").read_bytes()
        args = ["record", "T01", "--kind", "pass", "--summary", "未满足验收"]
        self.assertEqual(self.invoke(*args)[0], 1)
        self.assertEqual(self.invoke(*args, "--independent", "--evidence", "labs/missing.md")[0], 1)
        (self.root / "labs/empty.md").touch()
        self.assertEqual(self.invoke(*args, "--independent", "--evidence", "labs/empty.md")[0], 1)
        self.assertEqual((self.root / "learning/events.jsonl").read_bytes(), before)

    def test_reject_evidence_outside_repository(self):
        self.assertEqual(self.record(evidence="../outside.md")[0], 1)
        self.assertEqual(self.record(evidence=str(self.root / "labs/result.md"))[0], 1)

    def test_note_does_not_imply_learning_and_block_is_explicit(self):
        self.assertEqual(self.record("note")[0], 0)
        self.assertEqual(self.state()["T01"]["status"], "not_started")
        self.assertEqual(self.record("block")[0], 0)
        self.assertIn("阻塞：T01", self.invoke("next")[1])
        self.assertEqual(self.invoke("start", "T01")[0], 0)
        self.assertEqual(self.state()["T01"]["status"], "learning")

    def test_review_failure_and_recovery(self):
        self.assertEqual(self.record("review-pass")[0], 1)
        self.assertEqual(self.record()[0], 0)
        self.assertEqual(self.record()[0], 1)
        self.assertEqual(self.record("review-pass")[0], 0)
        self.assertEqual(self.state()["T01"]["review_index"], 1)
        self.assertEqual(self.record("review-fail")[0], 0)
        self.assertEqual(self.state()["T01"]["status"], "needs_work")
        self.assertEqual(self.record("review-pass")[0], 0)
        self.assertEqual(self.state()["T01"]["status"], "passed")
        self.assertEqual(self.state()["T01"]["review_index"], 0)

    def test_due_review_has_priority_over_new_task(self):
        self.assertEqual(self.record()[0], 0)
        _, curriculum, _ = study.load(self.root)
        due, _, fresh = study.recommendations(curriculum["tasks"], self.state(), date(2099, 1, 1))
        self.assertEqual(due[0]["id"], "T01")
        self.assertEqual(fresh[0]["id"], "T02")

    def test_correction_preserves_history_and_removes_false_pass(self):
        self.assertEqual(self.record()[0], 0)
        before = (self.root / "learning/events.jsonl").read_bytes()
        self.assertEqual(self.record("correction", state="learning")[0], 0)
        self.assertTrue((self.root / "learning/events.jsonl").read_bytes().startswith(before))
        self.assertEqual(self.state()["T01"]["status"], "learning")
        self.assertIsNone(self.state()["T01"]["due"])

    def test_reschedule_changes_plan_but_keeps_actual_events(self):
        self.assertEqual(self.record("attempt", minutes=25)[0], 0)
        before = (self.root / "learning/events.jsonl").read_bytes()
        self.assertEqual(self.invoke("reschedule", "--start", "2026-11-09")[0], 0)
        self.assertEqual((self.root / "learning/events.jsonl").read_bytes(), before)
        self.assertIn("2026-11-09", (self.root / "learning/TIMELINE.md").read_text())
        self.assertEqual(self.invoke("check")[0], 0)

    def test_corrupted_or_duplicate_log_fails_without_silent_repair(self):
        path = self.root / "learning/events.jsonl"
        path.write_text('{"truncated":', encoding="utf-8")
        before = path.read_bytes()
        self.assertEqual(self.invoke("start", "T01")[0], 1)
        self.assertEqual(path.read_bytes(), before)
        path.write_text("", encoding="utf-8")
        self.assertEqual(self.record()[0], 0)
        line = path.read_text()
        path.write_text(line + line, encoding="utf-8")
        self.assertIn("重复", self.invoke("check")[1])

    def test_stale_views_can_be_regenerated(self):
        self.assertEqual(self.invoke("render")[0], 0)
        (self.root / "learning/PROGRESS.md").write_text("stale", encoding="utf-8")
        self.assertEqual(self.invoke("check")[0], 1)
        self.assertEqual(self.invoke("render")[0], 0)
        self.assertEqual(self.invoke("check")[0], 0)

    def test_invalid_record_and_unknown_task_do_not_append(self):
        self.assertEqual(self.record("attempt", minutes=-1)[0], 1)
        self.assertEqual(self.invoke("start", "unknown")[0], 1)
        self.assertEqual((self.root / "learning/events.jsonl").read_bytes(), b"")


if __name__ == "__main__":
    unittest.main()
