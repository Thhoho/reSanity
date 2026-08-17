from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "validation/v2/run_final_ab_dsh.py"
PRELAYER_PATH = ROOT / "validation/v2/run_dsh_prelayers.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("resanity_final_ab_dsh", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load DSH final A/B runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_prelayer():
    spec = importlib.util.spec_from_file_location("resanity_dsh_prelayers", PRELAYER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load DSH prelayer runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DshFinalAbRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()
        cls.prelayer = load_prelayer()

    def make_profile_pair(self, raw: str) -> SimpleNamespace:
        root = Path(raw)
        dsh_home = root / "dsh-home"
        baseline = dsh_home / "profiles/headless-baseline"
        candidate = dsh_home / "profiles/headless-resanity"
        baseline.mkdir(parents=True)
        active_root = candidate / "node_modules/resanity"
        (active_root / "references").mkdir(parents=True)
        shared = {
            "private": True,
            "dependencies": {
                "shared-helper": "1.0.0",
                "resanity-validation-budget": "file:/tmp/budget-guard",
            },
            "dsh": {"profile": {"bundles": ["base", "headless"]}},
        }
        (baseline / "package.json").write_text(json.dumps(shared), encoding="utf-8")
        candidate_package = json.loads(json.dumps(shared))
        candidate_package["dependencies"]["resanity"] = "file:resanity.tgz"
        candidate_package["dsh"]["profile"]["bundles"].append("resanity")
        candidate.mkdir(parents=True, exist_ok=True)
        (candidate / "package.json").write_text(
            json.dumps(candidate_package), encoding="utf-8"
        )
        shutil.copy2(ROOT / "SKILL.md", active_root / "SKILL.md")
        for name in ("investing.md", "anchors.md", "formal-audit.md"):
            shutil.copy2(ROOT / "references" / name, active_root / "references" / name)
        return SimpleNamespace(
            dsh_home=dsh_home,
            baseline_profile="headless-baseline",
            candidate_profile="headless-resanity",
            active_skill=active_root / "SKILL.md",
            candidate_root=ROOT,
            isolated_user_home=root / "empty-home",
            dsh_bin="unused-dsh",
        )

    def test_profile_pair_allows_only_one_resanity_delta(self) -> None:
        baseline_dump = "- id: base\n  name: base\n- id: headless\n  name: headless\n"
        candidate_dump = (
            baseline_dump
            + "# == /tmp/headless-resanity/cordis.patch.yml\n"
            + "- id: resanity\n  name: resanity\n"
        )
        skill_sha = self.runner.BASE.sha256_file(ROOT / "SKILL.md")
        with tempfile.TemporaryDirectory() as raw:
            args = self.make_profile_pair(raw)
            with mock.patch.object(
                self.runner,
                "dump_config",
                side_effect=[baseline_dump, candidate_dump],
            ):
                receipt = self.runner.profile_pair_receipt(args, skill_sha)
        self.assertEqual(receipt["status"], "PASS")
        self.assertFalse(receipt["baseline_profile"]["resanity_active"])
        self.assertEqual(
            receipt["candidate_profile"]["active_skill_sha256"], skill_sha
        )
        self.assertEqual(set(receipt["canonical_identities"]), {"core", "investing"})

    def test_profile_pair_rejects_non_resanity_config_drift(self) -> None:
        baseline_dump = "- id: base\n  config:\n    value: 1\n"
        candidate_dump = (
            "- id: base\n  config:\n    value: 2\n"
            "- id: resanity\n  name: resanity\n"
        )
        skill_sha = self.runner.BASE.sha256_file(ROOT / "SKILL.md")
        with tempfile.TemporaryDirectory() as raw:
            args = self.make_profile_pair(raw)
            with mock.patch.object(
                self.runner,
                "dump_config",
                side_effect=[baseline_dump, candidate_dump],
            ):
                with self.assertRaises(self.runner.FinalAbError):
                    self.runner.profile_pair_receipt(args, skill_sha)

    def test_session_patch_disables_retry_and_subagents(self) -> None:
        patch = self.runner.session_patch(
            Path("/tmp/one-session"), max_tool_calls=7, max_web_searches=3
        )
        self.assertIn("id: session-persistence-jsonl", patch)
        self.assertIn("id: resanity-validation-budget", patch)
        self.assertNotIn("name: resanity-validation-budget", patch)
        self.assertIn("maxToolCalls: 7", patch)
        self.assertIn("maxWebSearches: 3", patch)
        for plugin_id in self.runner.DISABLED_RUNTIME_PLUGINS:
            self.assertIn(f"id: {plugin_id}\n  disabled: true", patch)
        self.assertIn("tool-subagent-control", self.runner.DISABLED_RUNTIME_PLUGINS)
        self.assertIn("tool-workflow", self.runner.DISABLED_RUNTIME_PLUGINS)
        self.assertIn("tool-ralph", self.runner.DISABLED_RUNTIME_PLUGINS)
        for plugin_id in self.runner.WATCH_DISABLED_RUNTIME_PLUGINS:
            self.assertIn(f"id: {plugin_id}\n  config:\n    watch: false", patch)
        self.assertEqual(
            self.runner.WATCH_ENVIRONMENT["CHOKIDAR_USEPOLLING"], "1"
        )

    def test_dsh_metrics_and_skill_invocation_come_from_raw_events(self) -> None:
        events = [
            {"type": "session", "id": "session-1", "cwd": "/tmp/work"},
            {
                "type": "request/header",
                "data": {
                    "header": {
                        "config": {
                            "provider": "provider-1",
                            "model": "model-1",
                            "reasoningEffort": "max",
                        },
                        "tools": [{"name": "skill"}, {"name": "web_search"}],
                    }
                },
            },
            {
                "type": "tool/call",
                "data": {
                    "name": "skill",
                    "arguments": json.dumps({"name": "resanity"}),
                },
            },
            {
                "type": "step/end",
                "data": {
                    "usage": {
                        "inputTokens": 100,
                        "outputTokens": 20,
                        "reasoningTokens": 5,
                        "cacheReadTokens": 60,
                    }
                },
            },
        ]
        metrics = self.runner.parse_dsh_metrics(events)
        self.assertEqual(metrics["provider"], "provider-1")
        self.assertEqual(metrics["model"], "model-1")
        self.assertEqual(metrics["input_tokens"], 100)
        self.assertEqual(metrics["cache_read_tokens"], 60)
        self.assertEqual(metrics["tool_calls"], 1)
        self.assertEqual(self.runner.skill_names(events), ["resanity"])

    def test_budget_guard_denials_are_attempts_not_executions(self) -> None:
        events = [
            {
                "type": "tool/call",
                "data": {"callId": "one", "name": "web_search", "arguments": "{}"},
            },
            {
                "type": "tool/result",
                "data": {
                    "message": {
                        "source": {"kind": "tool", "callId": "one"},
                        "content": [{"type": "text", "text": "ok"}],
                    }
                },
            },
            {
                "type": "tool/call",
                "data": {"callId": "two", "name": "web_search", "arguments": "{}"},
            },
            {
                "type": "tool/result",
                "data": {
                    "message": {
                        "source": {"kind": "tool", "callId": "two"},
                        "content": [
                            {
                                "type": "text",
                                "text": "Error: RESANITY_VALIDATION_BUDGET_WEB_LIMIT",
                            }
                        ],
                    }
                },
            },
        ]
        metrics = self.runner.parse_dsh_metrics(events)
        self.assertEqual(metrics["tool_call_attempts"], 2)
        self.assertEqual(metrics["tool_calls"], 1)
        self.assertEqual(metrics["web_search"], 1)
        self.assertEqual(metrics["budget_denied_tool_calls"], 1)

    def test_report_delivery_shape_rejects_tool_protocol_leaks(self) -> None:
        leaked = (
            "预算接近上限，随后交付。\n"
            "<｜｜DSML｜｜tool_calls>\n"
            "<｜｜DSML｜｜invoke name=\"write\">"
        )
        self.assertEqual(
            self.runner.report_delivery_failures(leaked),
            ["report_tool_protocol_leak"],
        )
        self.assertEqual(
            self.runner.report_delivery_failures(
                "# 根结论\n\n证据不足。\n\n# 来源表\n\n- E1"
            ),
            [],
        )
        self.assertEqual(
            self.runner.report_delivery_failures("  \n"), ["report_missing"]
        )

    def test_report_delivery_shape_rejects_process_only_stdout(self) -> None:
        process_only = (
            "Budget check: active-research cap reached; one remaining call is "
            "reserved for the required deliverable write."
        )
        self.assertEqual(
            self.runner.report_delivery_failures(process_only),
            ["report_process_only"],
        )

    def test_workspace_report_is_recovered_without_becoming_host_success(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            workspace = root / "workspace"
            workspace.mkdir()
            (workspace / "REPORT.md").write_text(
                "# 根结论\n\n证据不足。\n", encoding="utf-8"
            )
            destination = root / "artifacts" / "recovered-report.md"
            recovered = self.runner.recover_workspace_report(workspace, destination)
            self.assertIsNotNone(recovered)
            self.assertTrue(destination.is_file())
            self.assertEqual(recovered["path"], "recovered-report.md")
            self.assertEqual(
                recovered["sha256"], self.runner.BASE.sha256_file(destination)
            )

    def test_prelayer_failure_recovers_report_but_stays_host_incomplete(self) -> None:
        process_only = (
            "Budget check: active-research cap reached; one remaining call is "
            "reserved for the required deliverable write."
        )
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            output = root / "output"
            workspace = output / "workspaces" / "Q01"
            artifact = output / "cases" / "Q01"
            args = SimpleNamespace(
                output=output,
                dsh_bin="unused-dsh",
                dsh_home=root / "dsh-home",
                candidate_profile="headless-resanity",
                max_tool_calls=30,
                max_web_searches=15,
                max_non_cached_input_tokens=150_000,
                max_wall_seconds=900,
                zstd_bin="unused-zstd",
                expected_provider="deepseek-official",
                expected_model="deepseek-v4-pro",
                expected_reasoning_effort="max",
            )

            def failed_run(*_args, **kwargs):
                cwd = Path(kwargs["cwd"])
                (cwd / "REPORT.md").write_text(
                    "# 根结论\n\n已交付可读报告。\n", encoding="utf-8"
                )
                return SimpleNamespace(returncode=1, stdout=process_only, stderr="quota")

            with mock.patch.object(
                self.prelayer.subprocess, "run", side_effect=failed_run
            ):
                row = self.prelayer.run_session(
                    args=args,
                    case={
                        "id": "Q01",
                        "layer": "core_contract",
                        "profile": "core",
                        "mode": "closed",
                    },
                    prompt="frozen prompt",
                    workspace=workspace,
                    artifact=artifact,
                )

            self.assertFalse(row["host_complete"])
            self.assertFalse(row["report_present"])
            self.assertTrue(row["recovered_report"])
            self.assertIn("dsh_exit_code", row["mechanical_failures"])
            self.assertIn("report_process_only", row["mechanical_failures"])
            self.assertTrue((artifact / "stdout.md").is_file())
            self.assertFalse((artifact / "report.md").exists())
            self.assertTrue((artifact / "recovered-report.md").is_file())


if __name__ == "__main__":
    unittest.main()
