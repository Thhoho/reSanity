from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "validation" / "dsh-full" / "run-full-t.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("resanity_full_runner", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load full validation runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FullValidationRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()

    def test_source_check_is_portable_and_does_not_invoke_dsh(self) -> None:
        result = subprocess.run(
            [sys.executable, str(RUNNER_PATH), "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "SUITE_SOURCE_OK")
        self.assertEqual(payload["run_count"], 21)
        self.assertEqual(
            payload["phase_counts"],
            {"contract": 8, "field": 10, "longitudinal": 3},
        )

    def test_deleted_anchor_is_never_an_allowed_write(self) -> None:
        changes = [
            {"path": "anchors/topic.md", "type": "deleted", "sha256": "a" * 64},
            {"path": "anchors/index.md", "type": "modified", "sha256": "b" * 64},
            {"path": "report.md", "type": "created", "sha256": "c" * 64},
        ]
        allowed, unexpected = self.runner.classify_changes(changes, ["anchors/*.md"])
        self.assertEqual([row["path"] for row in allowed], ["anchors/index.md"])
        self.assertEqual(
            [row["path"] for row in unexpected],
            ["anchors/topic.md", "report.md"],
        )

    def test_suite_validation_rejects_shortened_matrix(self) -> None:
        suite_path = ROOT / "validation" / "dsh-full" / "suite.json"
        suite = json.loads(suite_path.read_text(encoding="utf-8"))
        suite["runs"] = suite["runs"][:-1]
        with self.assertRaises(self.runner.ValidationError):
            self.runner.validate_suite(suite)

    def test_lanes_parallelize_independent_runs_but_serialize_anchor_history(self) -> None:
        suite_path = ROOT / "validation" / "dsh-full" / "suite.json"
        suite = json.loads(suite_path.read_text(encoding="utf-8"))
        runs = self.runner.validate_suite(suite)
        lanes = self.runner.build_lanes(runs)
        self.assertEqual(len(lanes), 19)
        anchor_lane = [lane for lane in lanes if lane[0]["workspace_group"] == "A01"]
        self.assertEqual(len(anchor_lane), 1)
        self.assertEqual(
            [row["id"] for row in anchor_lane[0]],
            [
                "A01-T0-anchor-create",
                "A01-T1-anchor-update",
                "A01-T2-anchor-invalidate",
            ],
        )
        self.assertTrue(all(len(lane) == 1 for lane in lanes if lane is not anchor_lane[0]))

    def test_contract_phase_runs_end_to_end_with_a_mechanical_fake_host(self) -> None:
        fake_source = textwrap.dedent(
            r'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys
import uuid

if "--version" in sys.argv:
    print("0.1.0-rc.6")
    raise SystemExit(0)

patch = Path(sys.argv[sys.argv.index("--patch") + 1])
root_line = [line for line in patch.read_text(encoding="utf-8").splitlines() if "root:" in line][0]
session_root = Path(json.loads(root_line.split("root:", 1)[1].strip()))
session_dir = session_root / str(uuid.uuid4())
session_dir.mkdir(parents=True)
events = [
    {"type": "session", "version": 0, "id": session_dir.name, "createdAt": 1000, "cwd": os.getcwd()},
    {"type": "permission/preset", "time": 1001, "data": {"preset": "workspace-write"}},
    {"type": "sandbox/mode", "time": 1002, "data": {"mode": "workspace-write"}},
    {"type": "approval/policy", "time": 1003, "data": {"policy": "ask"}},
    {"type": "request/header", "time": 1004, "data": {"header": {"config": {"provider": "deepseek-official", "model": "deepseek-v4-pro", "reasoningEffort": "max"}, "tools": [{"name": "skill"}, {"name": "web_search"}]}}},
    {"type": "step/start", "time": 1005, "data": {}},
    {"type": "tool/call", "time": 1006, "data": {"name": "skill"}},
    {"type": "tool/result", "time": 1007, "data": {}},
    {"type": "assistant/message", "time": 1008, "data": {"usage": {"inputTokens": 10, "outputTokens": 5, "reasoningTokens": 2, "cacheReadTokens": 0}}},
]
(session_dir / "session.jsonl").write_text(
    "\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n",
    encoding="utf-8",
)
print("synthetic report")
'''
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            fake_dsh = temporary / "dsh"
            fake_dsh.write_text(fake_source, encoding="utf-8")
            fake_dsh.chmod(0o755)
            fake_home = temporary / "home"
            (fake_home / "profiles/headless").mkdir(parents=True)
            for relative in (
                "settings.yaml",
                "profiles/headless/package.json",
                "profiles/headless/cordis.patch.yml",
                ".credentials.yaml",
            ):
                path = fake_home / relative
                path.write_text("{}\n", encoding="utf-8")
            run_root = temporary / "run"
            environment = os.environ.copy()
            environment["DSH_BIN"] = str(fake_dsh)
            environment["DSH_HOME_BASE"] = str(fake_home)
            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER_PATH),
                    "--phase",
                    "contract",
                    "--jobs",
                    "3",
                    str(run_root),
                ],
                cwd=ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads((run_root / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["completed_runs"], 8)
            self.assertEqual(summary["host_passed"], 8)
            self.assertEqual(summary["jobs"], 3)
            self.assertEqual(summary["lane_count"], 8)
            self.assertEqual(summary["semantic_status"], "NOT_AUDITED")
            self.assertTrue(all(row["automatic_retries"] == 0 for row in summary["results"]))
            self.assertEqual(len(list((run_root / "sessions").iterdir())), 8)


if __name__ == "__main__":
    unittest.main()
