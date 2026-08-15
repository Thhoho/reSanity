from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "validation" / "dsh-pilot"


class ValidationContractTests(unittest.TestCase):
    def test_skill_requires_bounded_negative_claims(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "否定结论使用双边界契约",
            "检索结论：截至 [as-of]",
            "现实边界：这不证明现实中不存在",
            "沉默不是官方否定",
            "第二次官方否定",
            "主体、事项、重要性阈值和报告期间",
            "零命中必须限定对象和层级",
            "未证实不等于经济值为零",
            "as-of 是发布日期闸门",
            "可行动强度也受最弱证据约束",
            "最终语义报告不得出现模型估算的调用数",
        ):
            self.assertIn(marker, skill)

    def test_scored_prompts_forbid_model_owned_runtime_artifacts(self) -> None:
        for case in ("C01", "C02", "C03", "C04"):
            prompt = (PILOT / "prompts" / f"{case}-T-thin.md").read_text(encoding="utf-8")
            for marker in (
                "不要写任何文件",
                "不要生成 audit receipt",
                "30 次总工具调用",
                "15 次 Web 搜索",
                "900 秒墙钟时间",
                "不要启动后台任务",
                "主动研究最多使用 26 次工具调用",
                "不得自报/估算调用数、token、耗时",
            ):
                self.assertIn(marker, prompt, f"{case} missing {marker}")

    def test_negative_regressions_repeat_the_two_boundaries(self) -> None:
        for case in ("C01", "C04"):
            prompt = (PILOT / "prompts" / f"{case}-T-thin.md").read_text(encoding="utf-8")
            self.assertIn("检索结论：", prompt)
            self.assertIn("现实边界：", prompt)
            self.assertIn("官方否定", prompt)
            self.assertIn("重要性阈值", prompt)

    def test_runner_uses_host_owned_budgets_and_receipts(self) -> None:
        runner = (PILOT / "run-final-t.sh").read_text(encoding="utf-8")
        for marker in (
            "MAX_TOOL_CALLS=30",
            "MAX_WEB_SEARCH_CALLS=15",
            "MAX_TOKENS_TOTAL=150000",
            "MAX_WALL_SECONDS=900",
            "--format host-receipt",
            "verify_case_budget",
            "unexpected workspace artifacts",
        ):
            self.assertIn(marker, runner)
        self.assertNotIn("timeout 1800", runner)

    def test_full_suite_is_long_layered_and_one_shot(self) -> None:
        import json

        full = ROOT / "validation" / "dsh-full"
        suite = json.loads((full / "suite.json").read_text(encoding="utf-8"))
        runs = suite["runs"]
        self.assertEqual(len(runs), 21)
        self.assertEqual(
            {phase: sum(row["phase"] == phase for row in runs) for phase in (
                "contract", "field", "longitudinal"
            )},
            {"contract": 8, "field": 10, "longitudinal": 3},
        )
        self.assertEqual(len({row["id"] for row in runs}), 21)
        runner = (full / "run-full-t.py").read_text(encoding="utf-8")
        for marker in (
            '"automatic_retries": 0',
            '"semantic_status": "NOT_AUDITED"',
            "skill_tool_calls",
            "workspace-changes.json",
            "invoke_dsh(",
            "--jobs",
            "build_lanes(",
        ):
            self.assertIn(marker, runner)
        self.assertNotIn("repair_report", runner)
        self.assertNotIn("retry_run", runner)

    def test_internal_validation_corpus_is_not_in_package_files(self) -> None:
        import json

        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertNotIn("validation/", package["files"])
        self.assertIn("validation/README.md", package["files"])


if __name__ == "__main__":
    unittest.main()
