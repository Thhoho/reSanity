import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "validation" / "dsh-pilot" / "session-metrics.py"


class SessionMetricsTests(unittest.TestCase):
    def test_extracts_only_mechanical_session_data(self):
        events = [
            {
                "type": "session",
                "version": 0,
                "id": "session-test",
                "createdAt": 1000,
                "cwd": "/tmp/isolated/C01/T",
            },
            {"type": "permission/preset", "time": 1001, "data": {"preset": "workspace-write"}},
            {"type": "sandbox/mode", "time": 1002, "data": {"mode": "workspace-write"}},
            {"type": "approval/policy", "time": 1003, "data": {"policy": "ask"}},
            {
                "type": "request/header",
                "time": 1004,
                "data": {
                    "header": {
                        "config": {
                            "provider": "deepseek-official",
                            "model": "deepseek-v4-pro",
                            "reasoningEffort": "max",
                        },
                        "tools": [{"name": "web_search"}, {"name": "skill"}],
                    }
                },
            },
            {"type": "step/start", "time": 1005, "data": {}},
            {"type": "tool/call", "time": 1006, "data": {"name": "skill"}},
            {"type": "tool/result", "time": 1007, "data": {"secret": "do not emit me"}},
            {
                "type": "assistant/message",
                "time": 1008,
                "data": {
                    "usage": {
                        "inputTokens": 11,
                        "outputTokens": 7,
                        "reasoningTokens": 3,
                        "cacheReadTokens": 5,
                    },
                    "message": {"content": "do not emit me"},
                },
            },
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            session_path = Path(temporary_directory) / "raw-session.jsonl"
            session_path.write_text(
                "\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(session_path)],
                check=False,
                capture_output=True,
                text=True,
            )
            host_result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--format",
                    "host-receipt",
                    str(session_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("do not emit me", result.stdout)
        metrics = json.loads(result.stdout)
        self.assertEqual(metrics["session_id"], "session-test")
        self.assertEqual(metrics["session_cwd"], "/tmp/isolated/C01/T")
        self.assertEqual(metrics["available_tools"], ["skill", "web_search"])
        self.assertEqual(metrics["input_tokens"], 11)
        self.assertEqual(metrics["output_tokens"], 7)
        self.assertEqual(metrics["reasoning_tokens"], 3)
        self.assertEqual(metrics["cache_read_tokens"], 5)
        self.assertEqual(metrics["skill_tool_calls"], 1)
        self.assertEqual(metrics["tool_calls"], 1)
        self.assertEqual(metrics["tool_results"], 1)
        self.assertEqual(metrics["malformed_lines"], 0)
        self.assertEqual(host_result.returncode, 0, host_result.stderr)
        host_receipt = json.loads(host_result.stdout)
        self.assertEqual(host_receipt["schema_version"], "resanity.host-receipt.v1")
        self.assertEqual(host_receipt["host"], "dsh")
        self.assertEqual(host_receipt["model"], "deepseek-v4-pro")
        self.assertEqual(host_receipt["runtime"]["tokens_total"], 21)
        self.assertEqual(host_receipt["runtime"]["tool_calls"], 1)
        self.assertEqual(host_receipt["runtime"]["wall_seconds"], 1)
        self.assertEqual(host_receipt["budget_usage"]["web_search"], 0)
        self.assertEqual(host_receipt["raw_session"]["path"], "raw-session.jsonl")
        self.assertRegex(host_receipt["raw_session"]["sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
