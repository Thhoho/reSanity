#!/usr/bin/env python3
"""Run the frozen 21-session T-arm validation suite without semantic branching.

This runner owns isolation, one-shot execution, host metrics, file-change
contracts, and archival. It deliberately does not inspect research meaning,
repair reports, retry a run, or choose the next run based on model output.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime as dt
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import statistics
import subprocess
import sys
import time
from typing import Any


FULL_DIR = Path(__file__).resolve().parent
ROOT = FULL_DIR.parents[1]
SUITE_PATH = FULL_DIR / "suite.json"
METRICS_SCRIPT = ROOT / "validation" / "dsh-pilot" / "session-metrics.py"
METHOD_FILES = (
    Path("SKILL.md"),
    Path("scripts/free_market_observations.py"),
    Path("scripts/tier1_providers.py"),
    Path("tools/research_check.py"),
)
DEFAULT_DSH_BIN = Path(
    "/Users/xiaweiqi/.npm/_npx/1e7f6d9597241db0/node_modules/.bin/dsh"
)
DEFAULT_DSH_HOME_BASE = Path(
    "/Users/xiaweiqi/Documents/dsh-pilot-runs-2026-08-14/home"
)
PHASES = ("contract", "field", "longitudinal")


class ValidationError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValidationError(f"JSON root must be an object: {path}")
    return value


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def relative_to_root(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError as error:
        raise ValidationError(f"suite input escapes repository root: {path}") from error


def validate_suite(suite: dict[str, Any]) -> list[dict[str, Any]]:
    if suite.get("schema") != "resanity.dsh-full-suite.v1":
        raise ValidationError("suite schema mismatch")
    runtime = suite.get("runtime")
    if not isinstance(runtime, dict):
        raise ValidationError("suite.runtime must be an object")
    runs = suite.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValidationError("suite.runs must be a non-empty array")

    seen: set[str] = set()
    counts = {phase: 0 for phase in PHASES}
    longitudinal_positions: list[str] = []
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(runs):
        if not isinstance(raw, dict):
            raise ValidationError(f"run #{index + 1} must be an object")
        run_id = raw.get("id")
        if not isinstance(run_id, str) or not run_id or "/" in run_id or ".." in run_id:
            raise ValidationError(f"invalid run id at position {index + 1}: {run_id!r}")
        if run_id in seen:
            raise ValidationError(f"duplicate run id: {run_id}")
        seen.add(run_id)

        phase = raw.get("phase")
        if phase not in counts:
            raise ValidationError(f"invalid phase for {run_id}: {phase!r}")
        counts[phase] += 1
        if phase == "longitudinal":
            longitudinal_positions.append(run_id)

        prompt_value = raw.get("prompt")
        if not isinstance(prompt_value, str):
            raise ValidationError(f"{run_id}: prompt must be a string")
        prompt_path = (FULL_DIR / prompt_value).resolve()
        relative_to_root(prompt_path)
        if not prompt_path.is_file():
            raise ValidationError(f"{run_id}: prompt is missing: {prompt_path}")

        budgets = raw.get("budgets")
        if not isinstance(budgets, dict):
            raise ValidationError(f"{run_id}: budgets must be an object")
        for key in ("tool_calls", "web_search", "tokens_total", "wall_seconds"):
            value = budgets.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValidationError(f"{run_id}: invalid budget {key}={value!r}")

        fixtures: list[dict[str, str]] = []
        for fixture in raw.get("fixtures", []):
            if not isinstance(fixture, dict):
                raise ValidationError(f"{run_id}: fixture must be an object")
            source_value = fixture.get("source")
            dest_value = fixture.get("dest")
            if not isinstance(source_value, str) or not isinstance(dest_value, str):
                raise ValidationError(f"{run_id}: fixture source/dest must be strings")
            source = (FULL_DIR / source_value).resolve()
            relative_to_root(source)
            if not source.exists():
                raise ValidationError(f"{run_id}: fixture is missing: {source}")
            dest = Path(dest_value)
            if dest.is_absolute() or ".." in dest.parts or dest == Path("."):
                raise ValidationError(f"{run_id}: unsafe fixture destination: {dest}")
            fixtures.append({"source": str(source), "dest": dest.as_posix()})

        allowed_writes = raw.get("allowed_writes", [])
        if not isinstance(allowed_writes, list) or any(
            not isinstance(item, str) or item.startswith("/") or ".." in Path(item).parts
            for item in allowed_writes
        ):
            raise ValidationError(f"{run_id}: invalid allowed_writes")
        if phase != "longitudinal" and allowed_writes:
            raise ValidationError(f"{run_id}: only longitudinal runs may write semantic files")

        workspace_group = raw.get("workspace_group", run_id)
        if (
            not isinstance(workspace_group, str)
            or not workspace_group
            or "/" in workspace_group
            or ".." in workspace_group
        ):
            raise ValidationError(f"{run_id}: invalid workspace_group")

        item = dict(raw)
        item["prompt_source"] = str(prompt_path)
        item["fixtures_normalized"] = fixtures
        item["allowed_writes"] = allowed_writes
        item["workspace_group"] = workspace_group
        normalized.append(item)

    expected_counts = {"contract": 8, "field": 10, "longitudinal": 3}
    if counts != expected_counts:
        raise ValidationError(f"suite phase counts must be {expected_counts}, got {counts}")
    expected_longitudinal = [
        "A01-T0-anchor-create",
        "A01-T1-anchor-update",
        "A01-T2-anchor-invalidate",
    ]
    if longitudinal_positions != expected_longitudinal:
        raise ValidationError(
            "longitudinal runs must remain ordered T0 -> T1 -> T2; "
            f"got {longitudinal_positions}"
        )
    return normalized


def snapshot_files(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not root.exists():
        return result
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        result[path.relative_to(root).as_posix()] = sha256_file(path)
    return result


def diff_snapshots(before: dict[str, str], after: dict[str, str]) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    for path in sorted(set(before) | set(after)):
        if path not in before:
            changes.append({"path": path, "type": "created", "sha256": after[path]})
        elif path not in after:
            changes.append({"path": path, "type": "deleted", "sha256": before[path]})
        elif before[path] != after[path]:
            changes.append({"path": path, "type": "modified", "sha256": after[path]})
    return changes


def classify_changes(
    changes: list[dict[str, str]], allowed_patterns: list[str]
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    allowed: list[dict[str, str]] = []
    unexpected: list[dict[str, str]] = []
    for change in changes:
        permitted = change["type"] != "deleted" and any(
            fnmatch.fnmatchcase(change["path"], pattern) for pattern in allowed_patterns
        )
        (allowed if permitted else unexpected).append(change)
    return allowed, unexpected


def copy_fixture(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def session_files(root: Path) -> set[Path]:
    if not root.exists():
        return set()
    return {
        path.resolve()
        for path in root.rglob("*")
        if path.is_file() and path.name in {"session.jsonl", "session.jsonl.zstd"}
    }


def invoke_dsh(
    dsh_bin: Path,
    dsh_home: Path,
    patch_path: Path,
    workspace: Path,
    prompt: str,
    wall_seconds: int,
) -> tuple[int, str, str, int]:
    environment = os.environ.copy()
    environment["DSH_HOME"] = str(dsh_home)
    started = time.monotonic()
    process = subprocess.Popen(
        [str(dsh_bin), "--profile", "headless", "--patch", str(patch_path), prompt],
        cwd=workspace,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=wall_seconds)
        exit_code = int(process.returncode)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
        exit_code = 124
        stderr = (stderr or "") + f"\nHOST_TIMEOUT after {wall_seconds} seconds\n"
    elapsed = max(0, int(time.monotonic() - started))
    return exit_code, stdout or "", stderr or "", elapsed


def run_metrics(raw_session: Path, host_dir: Path) -> tuple[dict[str, Any] | None, str | None]:
    metrics_path = host_dir / "session-metrics.json"
    receipt_path = host_dir / "host-receipt.json"
    for output_path, extra in (
        (metrics_path, []),
        (receipt_path, ["--format", "host-receipt"]),
    ):
        command = [sys.executable, str(METRICS_SCRIPT), *extra, str(raw_session)]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        output_path.write_text(result.stdout, encoding="utf-8")
        if result.returncode != 0:
            (host_dir / "metrics-error.txt").write_text(
                f"command: {command!r}\nexit: {result.returncode}\n{result.stderr}",
                encoding="utf-8",
            )
            return None, f"session-metrics exited {result.returncode}"
    try:
        return read_json(metrics_path), None
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        return None, f"invalid metrics JSON: {error}"


def verify_environment(
    metrics: dict[str, Any], runtime: dict[str, Any], workspace: Path
) -> list[str]:
    expected = {
        "session_cwd": str(workspace.resolve()),
        "provider": runtime["provider"],
        "model": runtime["model"],
        "reasoning_effort": runtime["reasoning_effort"],
        "permission_preset": runtime["permission_preset"],
        "sandbox_mode": runtime["sandbox_mode"],
        "approval_policy": runtime["approval_policy"],
    }
    errors = [
        f"{name}: expected {value!r}, got {metrics.get(name)!r}"
        for name, value in expected.items()
        if metrics.get(name) != value
    ]
    tools = set(metrics.get("available_tools") or [])
    for tool in runtime.get("required_tools", []):
        if tool not in tools:
            errors.append(f"available_tools: missing {tool!r}")
    if metrics.get("skill_tool_calls") != 1:
        errors.append(
            f"skill_tool_calls: expected exactly 1, got {metrics.get('skill_tool_calls')!r}"
        )
    if metrics.get("malformed_lines") != 0:
        errors.append(f"malformed_lines: {metrics.get('malformed_lines')!r}")
    return errors


def verify_budget(
    host_receipt: dict[str, Any], budgets: dict[str, int], measured_wall: int
) -> tuple[list[str], dict[str, int]]:
    usage = host_receipt.get("budget_usage")
    if not isinstance(usage, dict):
        return ["host receipt budget_usage missing"], {}
    actual: dict[str, int] = {}
    errors: list[str] = []
    for name in ("tool_calls", "web_search", "tokens_total", "wall_seconds"):
        value = usage.get(name)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"{name}: invalid host usage {value!r}")
            continue
        if name == "wall_seconds":
            value = max(value, measured_wall)
        actual[name] = value
        if value > budgets[name]:
            errors.append(f"{name}: used {value}, limit {budgets[name]}")
    return errors, actual


def percentile_nearest(values: list[int], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int((len(ordered) * percentile + 0.999999)) - 1))
    return float(ordered[index])


def cost_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for phase in PHASES:
        rows = [row for row in results if row["phase"] == phase and row.get("usage")]
        phase_summary: dict[str, Any] = {"runs_with_metrics": len(rows)}
        for metric in ("tokens_total", "tool_calls", "web_search", "wall_seconds"):
            values = [int(row["usage"][metric]) for row in rows if metric in row["usage"]]
            phase_summary[metric] = {
                "median": statistics.median(values) if values else None,
                "p90_nearest_rank": percentile_nearest(values, 0.9),
            }
        output[phase] = phase_summary
    return output


def freeze_inputs(
    run_root: Path, runs: list[dict[str, Any]]
) -> tuple[Path, dict[str, dict[str, Any]], dict[str, str]]:
    frozen_method = run_root / "frozen-method"
    frozen_inputs = run_root / "frozen-inputs"
    frozen_method.mkdir(parents=True)
    frozen_inputs.mkdir(parents=True)

    hashes: dict[str, str] = {}
    for relative in METHOD_FILES:
        source = ROOT / relative
        if not source.is_file():
            raise ValidationError(f"method file missing: {source}")
        destination = frozen_method / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        hashes[relative.as_posix()] = sha256_file(destination)

    shutil.copy2(SUITE_PATH, frozen_inputs / "suite.json")
    hashes["validation/dsh-full/suite.json"] = sha256_file(frozen_inputs / "suite.json")

    frozen_runs: dict[str, dict[str, Any]] = {}
    for item in runs:
        run_id = item["id"]
        prompt_destination = frozen_inputs / "prompts" / f"{run_id}.md"
        prompt_destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(item["prompt_source"]), prompt_destination)
        hashes[f"prompt:{run_id}"] = sha256_file(prompt_destination)

        frozen_fixtures: list[dict[str, str]] = []
        for index, fixture in enumerate(item["fixtures_normalized"], start=1):
            source = Path(fixture["source"])
            frozen_source = frozen_inputs / "fixtures" / run_id / f"{index:02d}"
            copy_fixture(source, frozen_source)
            if frozen_source.is_dir():
                for path in sorted(entry for entry in frozen_source.rglob("*") if entry.is_file()):
                    key = f"fixture:{run_id}:{path.relative_to(frozen_source).as_posix()}"
                    hashes[key] = sha256_file(path)
            else:
                hashes[f"fixture:{run_id}:{source.name}"] = sha256_file(frozen_source)
            frozen_fixtures.append(
                {"source": str(frozen_source), "dest": fixture["dest"]}
            )
        frozen_runs[run_id] = {
            "prompt": str(prompt_destination),
            "fixtures": frozen_fixtures,
        }
    write_json(run_root / "frozen-manifest.json", hashes)
    return frozen_method, frozen_runs, hashes


def install_method(frozen_method: Path, workspace: Path) -> None:
    destination = workspace / ".dsh" / "skills" / "resanity"
    if destination.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(frozen_method, destination)


def build_lanes(runs: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Group shared-workspace runs into ordered lanes; independent runs stay alone."""
    lanes: list[list[dict[str, Any]]] = []
    lane_by_workspace: dict[str, list[dict[str, Any]]] = {}
    for item in runs:
        workspace_group = item["workspace_group"]
        lane = lane_by_workspace.get(workspace_group)
        if lane is None:
            lane = []
            lane_by_workspace[workspace_group] = lane
            lanes.append(lane)
        lane.append(item)
    return lanes


def jobs_value(value: str) -> int:
    try:
        jobs = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("jobs must be an integer") from error
    if not 1 <= jobs <= 8:
        raise argparse.ArgumentTypeError("jobs must be between 1 and 8")
    return jobs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_root", nargs="?", help="new absolute run-root path")
    parser.add_argument("--phase", choices=PHASES, help="debug one phase only")
    parser.add_argument(
        "--jobs",
        type=jobs_value,
        default=1,
        help="maximum concurrent DSH sessions (1-8; recommended: 3)",
    )
    parser.add_argument("--prepare-only", action="store_true", help="freeze and preflight only")
    parser.add_argument("--check", action="store_true", help="validate source suite without DSH")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    suite = read_json(SUITE_PATH)
    all_runs = validate_suite(suite)
    selected_runs = [run for run in all_runs if not args.phase or run["phase"] == args.phase]

    if args.check:
        if args.run_root or args.prepare_only or args.phase or args.jobs != 1:
            raise ValidationError(
                "--check cannot be combined with run_root, --phase, --jobs or --prepare-only"
            )
        method_hashes = {
            relative.as_posix(): sha256_file(ROOT / relative) for relative in METHOD_FILES
        }
        print(
            json.dumps(
                {
                    "status": "SUITE_SOURCE_OK",
                    "schema": suite["schema"],
                    "run_count": len(all_runs),
                    "phase_counts": {
                        phase: sum(run["phase"] == phase for run in all_runs)
                        for phase in PHASES
                    },
                    "suite_sha256": sha256_file(SUITE_PATH),
                    "method_hashes": method_hashes,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if not args.run_root:
        raise ValidationError("run_root is required unless --check is used")
    run_root_input = Path(args.run_root)
    if not run_root_input.is_absolute():
        raise ValidationError("run_root must be absolute")
    run_root = run_root_input.resolve()
    if run_root == Path("/") or ROOT == run_root or ROOT in run_root.parents:
        raise ValidationError(f"run_root must be outside repository: {ROOT}")
    if run_root.exists():
        raise ValidationError(f"run_root already exists: {run_root}")

    dsh_bin = Path(os.environ.get("DSH_BIN", str(DEFAULT_DSH_BIN))).resolve()
    dsh_home = Path(os.environ.get("DSH_HOME_BASE", str(DEFAULT_DSH_HOME_BASE))).resolve()
    if not dsh_bin.is_file() or not os.access(dsh_bin, os.X_OK):
        raise ValidationError(f"DSH binary missing/not executable: {dsh_bin}")
    required_runtime_files = (
        dsh_home / "settings.yaml",
        dsh_home / "profiles/headless/package.json",
        dsh_home / "profiles/headless/cordis.patch.yml",
        dsh_home / ".credentials.yaml",
    )
    for path in required_runtime_files:
        if not path.is_file():
            raise ValidationError(f"DSH runtime file missing: {path}")
    version_result = subprocess.run(
        [str(dsh_bin), "--version"], capture_output=True, text=True, check=False
    )
    actual_version = version_result.stdout.strip()
    expected_version = suite["runtime"]["dsh_version"]
    if version_result.returncode != 0 or actual_version != expected_version:
        raise ValidationError(
            f"DSH version mismatch: expected {expected_version!r}, got {actual_version!r}"
        )

    run_root.mkdir(parents=True)
    sessions_root = run_root / "sessions"
    session_patches_root = run_root / "session-patches"
    sessions_root.mkdir()
    session_patches_root.mkdir()
    frozen_method, frozen_runs, frozen_hashes = freeze_inputs(run_root, selected_runs)

    lanes = build_lanes(selected_runs)

    environment = {
        "schema": "resanity.dsh-full-environment.v1",
        "created_at": utc_now(),
        "source_root": str(ROOT),
        "run_root": str(run_root),
        "selected_phase": args.phase or "all",
        "selected_run_count": len(selected_runs),
        "jobs": args.jobs,
        "lane_count": len(lanes),
        "automatic_retries": 0,
        "prepare_only": bool(args.prepare_only),
        "runtime": suite["runtime"],
        "dsh_bin": str(dsh_bin),
        "dsh_home_base": str(dsh_home),
        "runtime_hashes": {
            str(path.relative_to(dsh_home)): sha256_file(path)
            for path in required_runtime_files
        },
        "runner_sha256": sha256_file(Path(__file__)),
        "metrics_script_sha256": sha256_file(METRICS_SCRIPT),
        "frozen_hashes": frozen_hashes,
    }
    write_json(run_root / "environment.json", environment)

    log_path = run_root / "run-log.md"
    log_path.write_text(
        "# reSanity full T validation\n\n"
        f"- Created: `{environment['created_at']}`\n"
        f"- Suite runs: `{len(selected_runs)}` (`{args.phase or 'all'}`)\n"
        f"- DSH: `{actual_version}`\n"
        f"- Skill SHA-256: `{frozen_hashes['SKILL.md']}`\n"
        f"- Concurrency: `{args.jobs}` jobs across `{len(lanes)}` dependency lanes\n"
        "- Automatic retries: `0`\n\n"
        "| Run | Phase | Exit | Wall | Session | Environment | Budget | Writes | Report |\n"
        "|---|---|---:|---:|---|---|---|---|---|\n",
        encoding="utf-8",
    )

    if args.prepare_only:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write("\nPrepared only; no model calls were made. This root cannot be resumed.\n")
        print(f"PREPARED: {run_root}")
        return 0

    runtime = suite["runtime"]
    workspaces_root = run_root / "workspaces"
    runs_root = run_root / "runs"

    position_by_id = {
        item["id"]: position for position, item in enumerate(selected_runs, start=1)
    }

    def execute_one(item: dict[str, Any]) -> dict[str, Any]:
        run_id = item["id"]
        phase = item["phase"]
        position = position_by_id[run_id]
        workspace = workspaces_root / item["workspace_group"] / "T"
        artifact_dir = runs_root / run_id / "T"
        host_dir = runs_root / run_id / "host"
        session_root = sessions_root / run_id
        session_patch = session_patches_root / f"{run_id}.yml"
        artifact_dir.mkdir(parents=True)
        host_dir.mkdir(parents=True)
        session_root.mkdir(parents=True)
        session_patch.write_text(
            "- id: session-persistence-jsonl\n"
            "  config:\n"
            f"    root: {json.dumps(str(session_root), ensure_ascii=False)}\n",
            encoding="utf-8",
        )
        install_method(frozen_method, workspace)

        frozen = frozen_runs[run_id]
        for fixture in frozen["fixtures"]:
            copy_fixture(Path(fixture["source"]), workspace / fixture["dest"])
        prompt_path = Path(frozen["prompt"])
        prompt = prompt_path.read_text(encoding="utf-8")
        shutil.copy2(prompt_path, artifact_dir / "prompt.md")

        before_workspace = snapshot_files(workspace)
        before_sessions = session_files(session_root)
        started_at = utc_now()
        print(f"RUNNING {position}/{len(selected_runs)}: {run_id} (one attempt)", flush=True)
        exit_code, stdout, stderr, measured_wall = invoke_dsh(
            dsh_bin,
            dsh_home,
            session_patch,
            workspace,
            prompt,
            int(item["budgets"]["wall_seconds"]),
        )
        ended_at = utc_now()
        (artifact_dir / "report.md").write_text(stdout, encoding="utf-8")
        (artifact_dir / "headless-final.txt").write_text(stdout, encoding="utf-8")
        (artifact_dir / "headless-stderr.txt").write_text(stderr, encoding="utf-8")

        after_workspace = snapshot_files(workspace)
        all_changes = diff_snapshots(before_workspace, after_workspace)
        allowed_changes, unexpected_changes = classify_changes(
            all_changes, list(item.get("allowed_writes", []))
        )
        write_json(
            host_dir / "workspace-changes.json",
            {
                "allowed_patterns": item.get("allowed_writes", []),
                "allowed": allowed_changes,
                "unexpected": unexpected_changes,
            },
        )

        new_sessions = sorted(session_files(session_root) - before_sessions)
        archive_status = "missing_or_ambiguous"
        environment_errors: list[str] = []
        budget_errors: list[str] = []
        metrics_error: str | None = None
        usage: dict[str, int] = {}
        raw_session_name: str | None = None
        if len(new_sessions) == 1:
            source_session = new_sessions[0]
            raw_session_name = (
                "raw-session.jsonl.zstd"
                if source_session.name.endswith(".zstd")
                else "raw-session.jsonl"
            )
            raw_session = host_dir / raw_session_name
            shutil.copy2(source_session, raw_session)
            metrics, metrics_error = run_metrics(raw_session, host_dir)
            if metrics is not None:
                archive_status = "archived"
                environment_errors = verify_environment(metrics, runtime, workspace)
                try:
                    receipt = read_json(host_dir / "host-receipt.json")
                    if receipt.get("schema_version") != "resanity.host-receipt.v1":
                        budget_errors.append("host receipt schema mismatch")
                    else:
                        budget_errors, usage = verify_budget(
                            receipt, item["budgets"], measured_wall
                        )
                except (OSError, json.JSONDecodeError, ValidationError) as error:
                    budget_errors.append(f"invalid host receipt: {error}")
            else:
                archive_status = "metrics_failed"

        output_error = None if stdout.strip() else "empty model stdout"
        passed = not any(
            (
                exit_code != 0,
                archive_status != "archived",
                bool(environment_errors),
                bool(budget_errors),
                bool(unexpected_changes),
                output_error is not None,
            )
        )
        result = {
            "id": run_id,
            "phase": phase,
            "workspace_group": item["workspace_group"],
            "started_at": started_at,
            "ended_at": ended_at,
            "dsh_exit_code": exit_code,
            "timed_out": exit_code == 124,
            "measured_wall_seconds": measured_wall,
            "prompt_sha256": sha256_file(artifact_dir / "prompt.md"),
            "skill_sha256": frozen_hashes["SKILL.md"],
            "session_count": len(new_sessions),
            "raw_session": raw_session_name,
            "archive_status": archive_status,
            "metrics_error": metrics_error,
            "environment_errors": environment_errors,
            "budget_errors": budget_errors,
            "unexpected_workspace_changes": unexpected_changes,
            "allowed_workspace_changes": allowed_changes,
            "output_error": output_error,
            "budgets": item["budgets"],
            "usage": usage,
            "automatic_retries": 0,
            "host_pass": passed,
        }
        write_json(host_dir / "run-meta.json", result)
        print(
            f"DONE {position}/{len(selected_runs)}: {run_id} "
            f"host={'PASS' if passed else 'FAIL'}",
            flush=True,
        )
        return result

    def execute_lane(lane: list[dict[str, Any]]) -> list[dict[str, Any]]:
        # Items in one lane share a workspace, so their declared order is a hard
        # dependency. Different lanes never share session roots or workspaces.
        return [execute_one(item) for item in lane]

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=args.jobs, thread_name_prefix="resanity") as executor:
        futures = [executor.submit(execute_lane, lane) for lane in lanes]
        for future in as_completed(futures):
            results.extend(future.result())
    results.sort(key=lambda row: position_by_id[row["id"]])

    with log_path.open("a", encoding="utf-8") as handle:
        for result in results:
            run_id = result["id"]
            archive_status = result["archive_status"]
            environment_errors = result["environment_errors"]
            budget_errors = result["budget_errors"]
            unexpected_changes = result["unexpected_workspace_changes"]
            if archive_status == "archived":
                environment_label = "verified" if not environment_errors else "mismatch"
                budget_label = "verified" if not budget_errors else "exceeded"
            else:
                environment_label = "not_checked"
                budget_label = "not_checked"
            writes_label = (
                "verified"
                if not unexpected_changes
                else f"unexpected:{len(unexpected_changes)}"
            )
            report_link = f"runs/{run_id}/T/report.md"
            handle.write(
                f"| {run_id} | {result['phase']} | {result['dsh_exit_code']} | "
                f"{result['measured_wall_seconds']} | {archive_status} | "
                f"{environment_label} | {budget_label} | {writes_label} | "
                f"[{run_id}]({report_link}) |\n"
            )

    phase_results = {
        phase: {
            "total": sum(row["phase"] == phase for row in results),
            "host_passed": sum(row["phase"] == phase and row["host_pass"] for row in results),
        }
        for phase in PHASES
    }
    summary = {
        "schema": "resanity.dsh-full-summary.v1",
        "created_at": environment["created_at"],
        "completed_at": utc_now(),
        "selected_phase": args.phase or "all",
        "jobs": args.jobs,
        "lane_count": len(lanes),
        "expected_runs": len(selected_runs),
        "completed_runs": len(results),
        "host_passed": sum(row["host_pass"] for row in results),
        "host_failed": sum(not row["host_pass"] for row in results),
        "phase_results": phase_results,
        "costs": cost_summary(results),
        "results": results,
        "semantic_status": "NOT_AUDITED",
        "automatic_retries": 0,
    }
    write_json(run_root / "summary.json", summary)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(
            f"\nCompleted {len(results)}/{len(selected_runs)} one-shot sessions; "
            f"host pass {summary['host_passed']}, fail {summary['host_failed']}.\n"
        )
        handle.write("Semantic status remains `NOT_AUDITED`; review reports separately.\n")

    if summary["host_failed"]:
        print(f"FAILED: {run_root}", file=sys.stderr)
        return 1
    print(f"COMPLETE: {run_root}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
