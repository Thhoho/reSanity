#!/bin/bash
# Run the four final T-arm cases once each in isolated workspaces and archive receipts.

set -eu
set -o pipefail

EXPECTED_SKILL_SHA256="8d9dfb8ada23a5390ed89b2f9d3b0fe426d37bce068baac3b5f69894d26e293d"
EXPECTED_FREE_MARKET_SHA256="407689f7db484503c7934f79d79aa1b1bbe23f07bd7ed5e75eeed0f519cffb6d"
EXPECTED_TIER1_SHA256="296276e3adb2a3cfd2233a5017c9677e0858ab2eca115b315aebb8a17cdaaa1e"
EXPECTED_RESEARCH_CHECK_SHA256="39a8c5e643bdd69140fab22bfd1da2de457e19a80c9673c1b93c8e9f7d4741f5"
EXPECTED_C01_PROMPT_SHA256="438cf9b431edfd0c16f2f03c15a0b9df30a4dd8eed4aba56e446e22c0b2e77e8"
EXPECTED_C02_PROMPT_SHA256="f3fb602851269fe6c4344f6b64886cacdde6da57fb25aec4ce4c19727b5cc1d6"
EXPECTED_C03_PROMPT_SHA256="8f829c41d7d758705d8d5e1876da90a08ce16d4acdf9a0df1f482fefe27b2b09"
EXPECTED_C04_PROMPT_SHA256="c9cf3a42a4ba7c588be95fdc4a0efd9b13d1c7212ea77ecef58b4f12efab586d"
EXPECTED_DSH_VERSION="0.1.0-rc.6"
EXPECTED_SETTINGS_SHA256="2e769225e9ba6ccd084f8a6c4e86add7b08dafe4f58036fefcab1e1aee8e5d4c"
EXPECTED_PROFILE_SHA256="563c0b6082748a6e93daad51514f01335c51fc9c44f5f88253383f18ac2557b5"
EXPECTED_PROFILE_PATCH_SHA256="ef189a8c27db6d63930aa3046a3040482e952eafcb7487c644d508e8d461f027"
EXPECTED_PROVIDER="deepseek-official"
EXPECTED_MODEL="deepseek-v4-pro"
EXPECTED_REASONING_EFFORT="max"
EXPECTED_PERMISSION_PRESET="workspace-write"
EXPECTED_SANDBOX_MODE="workspace-write"
EXPECTED_APPROVAL_POLICY="ask"

# Frozen host-owned validation budgets. The wall budget is enforced during the
# run; the remaining dimensions are measured from the archived raw session and
# fail the runner after all four one-shot cases have been preserved.
MAX_TOOL_CALLS=30
MAX_WEB_SEARCH_CALLS=15
MAX_TOKENS_TOTAL=150000
MAX_WALL_SECONDS=900

DEFAULT_DSH_BIN="/Users/xiaweiqi/.npm/_npx/1e7f6d9597241db0/node_modules/.bin/dsh"
DEFAULT_DSH_HOME_BASE="/Users/xiaweiqi/Documents/dsh-pilot-runs-2026-08-14/home"
DSH_BIN="${DSH_BIN:-$DEFAULT_DSH_BIN}"
DSH_HOME_BASE="${DSH_HOME_BASE:-$DEFAULT_DSH_HOME_BASE}"

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat >&2 <<'EOF'
Usage:
  run-final-t.sh [--prepare-only] /absolute/path/to/a-new-run-root

The run root must not already exist and must be outside the reSanity repository.
--prepare-only performs every mechanical preflight and creates workspaces, but
does not invoke the model. Use a disposable path for that mode.

Each case is limited to 30 total tool calls, 15 Web searches, 150000 non-cache
tokens, and 900 wall seconds. A budget failure is archived and never retried.
EOF
  exit 2
}

sha256() {
  shasum -a 256 "$1" | awk '{print $1}'
}

expected_prompt_sha256() {
  case "$1" in
    C01) printf '%s\n' "$EXPECTED_C01_PROMPT_SHA256" ;;
    C02) printf '%s\n' "$EXPECTED_C02_PROMPT_SHA256" ;;
    C03) printf '%s\n' "$EXPECTED_C03_PROMPT_SHA256" ;;
    C04) printf '%s\n' "$EXPECTED_C04_PROMPT_SHA256" ;;
    *) fail "unknown case: $1" ;;
  esac
}

canonical_path() {
  python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$1"
}

write_environment_json() {
  python3 - "$RUN_ROOT/environment.json" "$CREATED_AT" "$SOURCE_ROOT" "$RUN_ROOT" \
    "$DSH_BIN" "$DSH_HOME_BASE" "$ACTUAL_DSH_VERSION" "$SOURCE_SKILL_SHA256" \
    "$SETTINGS_SHA256" "$PROFILE_SHA256" "$PROFILE_PATCH_SHA256" "$RUNNER_SHA256" \
    "$METRICS_SCRIPT_SHA256" "$PREPARE_ONLY" "$MAX_TOOL_CALLS" \
    "$MAX_WEB_SEARCH_CALLS" "$MAX_TOKENS_TOTAL" "$MAX_WALL_SECONDS" <<'PY'
import json
import sys

(
    output,
    created_at,
    source_root,
    run_root,
    dsh_bin,
    dsh_home_base,
    dsh_version,
    skill_sha256,
    settings_sha256,
    profile_sha256,
    profile_patch_sha256,
    runner_sha256,
    metrics_script_sha256,
    prepare_only,
    max_tool_calls,
    max_web_search_calls,
    max_tokens_total,
    max_wall_seconds,
) = sys.argv[1:]
payload = {
    "schema": "resanity.dsh-final-t-environment.v1",
    "created_at": created_at,
    "source_root": source_root,
    "run_root": run_root,
    "dsh_bin": dsh_bin,
    "dsh_home_base": dsh_home_base,
    "dsh_version": dsh_version,
    "skill_sha256": skill_sha256,
    "settings_sha256": settings_sha256,
    "headless_profile_sha256": profile_sha256,
    "headless_profile_patch_sha256": profile_patch_sha256,
    "runner_sha256": runner_sha256,
    "metrics_script_sha256": metrics_script_sha256,
    "provider": "deepseek-official",
    "model": "deepseek-v4-pro",
    "reasoning_effort": "max",
    "budgets": {
        "tool_calls": int(max_tool_calls),
        "web_search": int(max_web_search_calls),
        "tokens_total": int(max_tokens_total),
        "wall_seconds": int(max_wall_seconds),
    },
    "timeout_seconds_per_case": int(max_wall_seconds),
    "prepare_only": prepare_only == "1",
    "automatic_retries": 0,
}
with open(output, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
    handle.write("\n")
PY
}

write_run_meta() {
  python3 - "$HOST_DIR/run-meta.json" "$CASE" "$START_ISO" "$END_ISO" "$WALL_SEC" \
    "$DSH_EXIT" "$ACTUAL_DSH_VERSION" "$WS" "$PROMPT_PATH" "$PROMPT_SHA256" \
    "$SOURCE_SKILL_SHA256" "$INSTALLED_SKILL_SHA256" "$ARCHIVE_STATUS" \
    "$ENVIRONMENT_STATUS" "$SESSION_SOURCE" "$RAW_SESSION_NAME" \
    "$HOST_RECEIPT_NAME" "$BUDGET_STATUS" "$MODEL_ARTIFACT_STATUS" \
    "$MAX_TOOL_CALLS" "$MAX_WEB_SEARCH_CALLS" "$MAX_TOKENS_TOTAL" \
    "$MAX_WALL_SECONDS" <<'PY'
import json
import sys

(
    output,
    case,
    started_at,
    ended_at,
    wall_sec,
    exit_code,
    dsh_version,
    workspace,
    prompt_path,
    prompt_sha256,
    source_skill_sha256,
    installed_skill_sha256,
    archive_status,
    environment_status,
    session_source,
    raw_session_name,
    host_receipt_name,
    budget_status,
    model_artifact_status,
    max_tool_calls,
    max_web_search_calls,
    max_tokens_total,
    max_wall_seconds,
) = sys.argv[1:]
payload = {
    "schema": "resanity.dsh-final-t-run.v1",
    "case": case,
    "arm": "T",
    "started_at": started_at,
    "ended_at": ended_at,
    "wall_seconds": int(wall_sec),
    "dsh_exit_code": int(exit_code),
    "timed_out": int(exit_code) == 124,
    "dsh_version": dsh_version,
    "workspace": workspace,
    "prompt_path": prompt_path,
    "prompt_sha256": prompt_sha256,
    "source_skill_sha256": source_skill_sha256,
    "installed_skill_sha256": installed_skill_sha256,
    "archive_status": archive_status,
    "environment_status": environment_status,
    "session_source": session_source or None,
    "raw_session": raw_session_name or None,
    "metrics": "session-metrics.json" if archive_status == "archived" else None,
    "host_receipt": host_receipt_name or None,
    "budget_status": budget_status,
    "model_artifact_status": model_artifact_status,
    "budgets": {
        "tool_calls": int(max_tool_calls),
        "web_search": int(max_web_search_calls),
        "tokens_total": int(max_tokens_total),
        "wall_seconds": int(max_wall_seconds),
    },
    "automatic_retries": 0,
}
with open(output, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
    handle.write("\n")
PY
}

verify_session_environment() {
  python3 - "$HOST_DIR/session-metrics.json" "$WS" "$EXPECTED_PROVIDER" "$EXPECTED_MODEL" \
    "$EXPECTED_REASONING_EFFORT" "$EXPECTED_PERMISSION_PRESET" "$EXPECTED_SANDBOX_MODE" \
    "$EXPECTED_APPROVAL_POLICY" <<'PY'
import json
import sys

(
    metrics_path,
    expected_cwd,
    expected_provider,
    expected_model,
    expected_effort,
    expected_permission,
    expected_sandbox,
    expected_approval,
) = sys.argv[1:]
with open(metrics_path, encoding="utf-8") as handle:
    metrics = json.load(handle)
checks = {
    "session_cwd": expected_cwd,
    "provider": expected_provider,
    "model": expected_model,
    "reasoning_effort": expected_effort,
    "permission_preset": expected_permission,
    "sandbox_mode": expected_sandbox,
    "approval_policy": expected_approval,
}
errors = [
    f"{key}: expected {expected!r}, got {metrics.get(key)!r}"
    for key, expected in checks.items()
    if metrics.get(key) != expected
]
tools = set(metrics.get("available_tools") or [])
for required in ("skill", "web_search"):
    if required not in tools:
        errors.append(f"available_tools: missing {required!r}")
if metrics.get("malformed_lines") != 0:
    errors.append(f"malformed_lines: expected 0, got {metrics.get('malformed_lines')!r}")
if errors:
    print("session environment mismatch:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)
PY
}

verify_case_budget() {
  python3 - "$HOST_DIR/host-receipt.json" "$MAX_TOOL_CALLS" "$MAX_WEB_SEARCH_CALLS" \
    "$MAX_TOKENS_TOTAL" "$MAX_WALL_SECONDS" <<'PY'
import json
import sys

path, tool_limit, search_limit, token_limit, wall_limit = sys.argv[1:]
with open(path, encoding="utf-8") as handle:
    receipt = json.load(handle)
if receipt.get("schema_version") != "resanity.host-receipt.v1":
    print("- host receipt schema mismatch", file=sys.stderr)
    raise SystemExit(1)
usage = receipt.get("budget_usage")
if not isinstance(usage, dict):
    print("- host receipt budget_usage missing", file=sys.stderr)
    raise SystemExit(1)
limits = {
    "tool_calls": int(tool_limit),
    "web_search": int(search_limit),
    "tokens_total": int(token_limit),
    "wall_seconds": int(wall_limit),
}
errors = []
for name, limit in limits.items():
    used = usage.get(name)
    if not isinstance(used, int) or isinstance(used, bool) or used < 0:
        errors.append(f"{name}: missing or invalid host usage {used!r}")
    elif used > limit:
        errors.append(f"{name}: used {used}, limit {limit}")
if errors:
    print("case budget exceeded:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)
PY
}

PREPARE_ONLY=0
if [ "${1:-}" = "--prepare-only" ]; then
  PREPARE_ONLY=1
  shift
fi
[ "$#" -eq 1 ] || usage

RUN_ROOT_INPUT=$1
case "$RUN_ROOT_INPUT" in
  /*) ;;
  *) fail "run root must be an absolute path" ;;
esac

for command_name in awk cat cmp comm cp date dirname find mkdir python3 sed shasum sort timeout zstd; do
  command -v "$command_name" >/dev/null 2>&1 || fail "required command not found: $command_name"
done

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SOURCE_ROOT=$(canonical_path "$SCRIPT_DIR/../..")
RUN_ROOT=$(canonical_path "$RUN_ROOT_INPUT")
DSH_BIN=$(canonical_path "$DSH_BIN")
DSH_HOME_BASE=$(canonical_path "$DSH_HOME_BASE")

[ "$RUN_ROOT" != "/" ] || fail "run root cannot be /"
case "$RUN_ROOT/" in
  "$SOURCE_ROOT/"*) fail "run root must be outside the reSanity repository: $SOURCE_ROOT" ;;
esac
[ ! -e "$RUN_ROOT" ] || fail "run root already exists; choose a new path: $RUN_ROOT"

[ -x "$DSH_BIN" ] || fail "DSH binary is missing or not executable: $DSH_BIN"
[ -d "$DSH_HOME_BASE" ] || fail "DSH home is missing: $DSH_HOME_BASE"
[ -f "$DSH_HOME_BASE/settings.yaml" ] || fail "DSH settings are missing"
[ -f "$DSH_HOME_BASE/profiles/headless/package.json" ] || fail "headless profile is missing"
[ -f "$DSH_HOME_BASE/profiles/headless/cordis.patch.yml" ] || fail "headless profile patch is missing"
[ -f "$DSH_HOME_BASE/.credentials.yaml" ] || fail "DSH credentials are missing"

ACTUAL_DSH_VERSION=$("$DSH_BIN" --version 2>/dev/null) || fail "could not read DSH version"
[ "$ACTUAL_DSH_VERSION" = "$EXPECTED_DSH_VERSION" ] || \
  fail "DSH version mismatch: expected $EXPECTED_DSH_VERSION, got $ACTUAL_DSH_VERSION"

SOURCE_SKILL_SHA256=$(sha256 "$SOURCE_ROOT/SKILL.md")
[ "$SOURCE_SKILL_SHA256" = "$EXPECTED_SKILL_SHA256" ] || \
  fail "SKILL.md hash mismatch: expected $EXPECTED_SKILL_SHA256, got $SOURCE_SKILL_SHA256"
[ "$(sha256 "$SOURCE_ROOT/scripts/free_market_observations.py")" = "$EXPECTED_FREE_MARKET_SHA256" ] || \
  fail "free_market_observations.py changed; refusing to mix method bundles"
[ "$(sha256 "$SOURCE_ROOT/scripts/tier1_providers.py")" = "$EXPECTED_TIER1_SHA256" ] || \
  fail "tier1_providers.py changed; refusing to mix method bundles"
[ "$(sha256 "$SOURCE_ROOT/tools/research_check.py")" = "$EXPECTED_RESEARCH_CHECK_SHA256" ] || \
  fail "research_check.py changed; refusing to mix method bundles"

SETTINGS_SHA256=$(sha256 "$DSH_HOME_BASE/settings.yaml")
PROFILE_SHA256=$(sha256 "$DSH_HOME_BASE/profiles/headless/package.json")
PROFILE_PATCH_SHA256=$(sha256 "$DSH_HOME_BASE/profiles/headless/cordis.patch.yml")
[ "$SETTINGS_SHA256" = "$EXPECTED_SETTINGS_SHA256" ] || \
  fail "DSH settings changed; refusing to mix runtime configurations"
[ "$PROFILE_SHA256" = "$EXPECTED_PROFILE_SHA256" ] || \
  fail "headless profile changed; refusing to mix runtime configurations"
[ "$PROFILE_PATCH_SHA256" = "$EXPECTED_PROFILE_PATCH_SHA256" ] || \
  fail "headless profile patch changed; refusing to mix runtime configurations"

for source_file in \
  "$SOURCE_ROOT/scripts/free_market_observations.py" \
  "$SOURCE_ROOT/scripts/tier1_providers.py" \
  "$SOURCE_ROOT/tools/research_check.py" \
  "$SCRIPT_DIR/session-metrics.py"; do
  [ -f "$source_file" ] || fail "required source file is missing: $source_file"
done
for case_name in C01 C02 C03 C04; do
  [ -f "$SCRIPT_DIR/prompts/$case_name-T-thin.md" ] || \
    fail "prompt is missing: $SCRIPT_DIR/prompts/$case_name-T-thin.md"
  [ "$(sha256 "$SCRIPT_DIR/prompts/$case_name-T-thin.md")" = "$(expected_prompt_sha256 "$case_name")" ] || \
    fail "$case_name prompt hash changed; refusing to mix prompt versions"
done

mkdir -p "$RUN_ROOT/.runner-output" "$RUN_ROOT/sessions"
SESSION_ROOT="$RUN_ROOT/sessions"
SESSION_PATCH="$RUN_ROOT/session-root.patch.yml"
python3 - "$SESSION_PATCH" "$SESSION_ROOT" <<'PY'
import json
import sys

with open(sys.argv[1], "w", encoding="utf-8") as handle:
    handle.write("- id: session-persistence-jsonl\n")
    handle.write("  config:\n")
    handle.write(f"    root: {json.dumps(sys.argv[2], ensure_ascii=False)}\n")
PY

CREATED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
RUNNER_SHA256=$(sha256 "$SCRIPT_DIR/run-final-t.sh")
METRICS_SCRIPT_SHA256=$(sha256 "$SCRIPT_DIR/session-metrics.py")
printf '%s\n' "$ACTUAL_DSH_VERSION" > "$RUN_ROOT/dsh-version.txt"
write_environment_json

cat > "$RUN_ROOT/run-log.md" <<EOF
# reSanity final T rerun

- Created: \`$CREATED_AT\`
- Skill SHA-256: \`$SOURCE_SKILL_SHA256\`
- DSH: \`$ACTUAL_DSH_VERSION\`
- Mode: \`$([ "$PREPARE_ONLY" -eq 1 ] && printf 'prepare-only' || printf 'run-once')\`
- Automatic retries: \`0\`

| Case | DSH exit | Wall seconds | Session archive | Runtime | Budget | Workspace writes | Report |
|---|---:|---:|---|---|---|---|---|
EOF

for CASE in C01 C02 C03 C04; do
  WS="$RUN_ROOT/$CASE/T"
  HOST_DIR="$RUN_ROOT/$CASE/host"
  SKILL_DEST="$WS/.dsh/skills/resanity"
  PROMPT_PATH="$SCRIPT_DIR/prompts/$CASE-T-thin.md"
  mkdir -p "$SKILL_DEST/scripts" "$SKILL_DEST/tools" "$HOST_DIR"
  cp "$SOURCE_ROOT/SKILL.md" "$SKILL_DEST/SKILL.md"
  cp "$SOURCE_ROOT/scripts/free_market_observations.py" "$SKILL_DEST/scripts/"
  cp "$SOURCE_ROOT/scripts/tier1_providers.py" "$SKILL_DEST/scripts/"
  cp "$SOURCE_ROOT/tools/research_check.py" "$SKILL_DEST/tools/"
  cp "$PROMPT_PATH" "$WS/prompt.md"

  INSTALLED_SKILL_SHA256=$(sha256 "$SKILL_DEST/SKILL.md")
  [ "$INSTALLED_SKILL_SHA256" = "$SOURCE_SKILL_SHA256" ] || \
    fail "$CASE installed Skill hash mismatch"
  PROMPT_SHA256=$(sha256 "$WS/prompt.md")

  (
    cd "$SKILL_DEST" || exit 1
    find . -type f -print | LC_ALL=C sort | while IFS= read -r method_file; do
      shasum -a 256 "$method_file"
    done
  ) > "$RUN_ROOT/.runner-output/$CASE-method-manifest.sha256" || \
    fail "$CASE could not create method manifest"

  if [ "$CASE" = "C01" ]; then
    cp "$RUN_ROOT/.runner-output/$CASE-method-manifest.sha256" "$RUN_ROOT/method-manifest.sha256"
  else
    cmp -s "$RUN_ROOT/method-manifest.sha256" "$RUN_ROOT/.runner-output/$CASE-method-manifest.sha256" || \
      fail "$CASE method bundle differs from C01"
  fi
done

if [ "$PREPARE_ONLY" -eq 1 ]; then
  printf '\nPrepared only; no model calls were made.\n' >> "$RUN_ROOT/run-log.md"
  printf 'PREPARED: %s\n' "$RUN_ROOT"
  exit 0
fi

ANY_VALIDATION_FAILURE=0
for CASE in C01 C02 C03 C04; do
  WS="$RUN_ROOT/$CASE/T"
  HOST_DIR="$RUN_ROOT/$CASE/host"
  PROMPT_PATH="$SCRIPT_DIR/prompts/$CASE-T-thin.md"
  PROMPT_SHA256=$(sha256 "$WS/prompt.md")
  INSTALLED_SKILL_SHA256=$(sha256 "$WS/.dsh/skills/resanity/SKILL.md")
  PROMPT_TEXT=$(<"$WS/prompt.md")
  STDOUT_PATH="$RUN_ROOT/.runner-output/$CASE-headless-final.txt"
  STDERR_PATH="$RUN_ROOT/.runner-output/$CASE-headless-stderr.txt"
  BEFORE_LIST="$RUN_ROOT/.runner-output/$CASE-sessions-before.txt"
  AFTER_LIST="$RUN_ROOT/.runner-output/$CASE-sessions-after.txt"
  NEW_LIST="$RUN_ROOT/.runner-output/$CASE-sessions-new.txt"
  WORKSPACE_BEFORE="$RUN_ROOT/.runner-output/$CASE-workspace-before.txt"
  WORKSPACE_AFTER="$RUN_ROOT/.runner-output/$CASE-workspace-after.txt"
  MODEL_ARTIFACT_LIST="$RUN_ROOT/.runner-output/$CASE-model-artifacts.txt"

  find "$SESSION_ROOT" -type f \( -name 'session.jsonl' -o -name 'session.jsonl.zstd' \) -print | \
    LC_ALL=C sort > "$BEFORE_LIST"
  find "$WS" -type f -print | LC_ALL=C sort > "$WORKSPACE_BEFORE"

  printf 'RUNNING: %s/T (one attempt)\n' "$CASE"
  START_EPOCH=$(date +%s)
  START_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  set +e
  (
    cd "$WS" || exit 125
    DSH_HOME="$DSH_HOME_BASE" timeout "$MAX_WALL_SECONDS" "$DSH_BIN" --profile headless \
      --patch "$SESSION_PATCH" "$PROMPT_TEXT"
  ) > "$STDOUT_PATH" 2> "$STDERR_PATH"
  DSH_EXIT=$?
  set -e
  if [ "$DSH_EXIT" -ne 0 ]; then
    ANY_VALIDATION_FAILURE=1
  fi
  END_EPOCH=$(date +%s)
  END_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  WALL_SEC=$((END_EPOCH - START_EPOCH))

  find "$WS" -type f -print | LC_ALL=C sort > "$WORKSPACE_AFTER"
  comm -13 "$WORKSPACE_BEFORE" "$WORKSPACE_AFTER" > "$MODEL_ARTIFACT_LIST"
  MODEL_ARTIFACT_COUNT=$(awk 'END {print NR + 0}' "$MODEL_ARTIFACT_LIST")
  if [ "$MODEL_ARTIFACT_COUNT" -eq 0 ]; then
    MODEL_ARTIFACT_STATUS="verified"
  else
    MODEL_ARTIFACT_STATUS="unexpected:$MODEL_ARTIFACT_COUNT"
    ANY_VALIDATION_FAILURE=1
  fi

  cp "$STDOUT_PATH" "$WS/headless-final.txt"
  cp "$STDOUT_PATH" "$WS/report.md"
  cp "$STDERR_PATH" "$WS/headless-stderr.txt"

  find "$SESSION_ROOT" -type f \( -name 'session.jsonl' -o -name 'session.jsonl.zstd' \) -print | \
    LC_ALL=C sort > "$AFTER_LIST"
  comm -13 "$BEFORE_LIST" "$AFTER_LIST" > "$NEW_LIST"
  NEW_SESSION_COUNT=$(awk 'END {print NR + 0}' "$NEW_LIST")

  ARCHIVE_STATUS="missing_or_ambiguous"
  ENVIRONMENT_STATUS="not_checked"
  BUDGET_STATUS="not_checked"
  SESSION_SOURCE=""
  RAW_SESSION_NAME=""
  HOST_RECEIPT_NAME=""
  if [ "$NEW_SESSION_COUNT" -eq 1 ]; then
    SESSION_SOURCE=$(sed -n '1p' "$NEW_LIST")
    case "$SESSION_SOURCE" in
      *.zstd) RAW_SESSION_NAME="raw-session.jsonl.zstd" ;;
      *) RAW_SESSION_NAME="raw-session.jsonl" ;;
    esac
    cp "$SESSION_SOURCE" "$HOST_DIR/$RAW_SESSION_NAME"
    if python3 "$SCRIPT_DIR/session-metrics.py" "$HOST_DIR/$RAW_SESSION_NAME" > "$HOST_DIR/session-metrics.json" && \
       python3 "$SCRIPT_DIR/session-metrics.py" --format host-receipt \
         "$HOST_DIR/$RAW_SESSION_NAME" > "$HOST_DIR/host-receipt.json"; then
      ARCHIVE_STATUS="archived"
      HOST_RECEIPT_NAME="host-receipt.json"
      if verify_session_environment; then
        ENVIRONMENT_STATUS="verified"
      else
        ENVIRONMENT_STATUS="mismatch"
      fi
      if verify_case_budget; then
        BUDGET_STATUS="verified"
      else
        BUDGET_STATUS="exceeded"
        ANY_VALIDATION_FAILURE=1
      fi
    else
      ARCHIVE_STATUS="metrics_failed"
    fi
  fi

  write_run_meta
  printf '| %s | %s | %s | %s | %s | %s | %s | [%s/T/report.md](%s/T/report.md) |\n' \
    "$CASE" "$DSH_EXIT" "$WALL_SEC" "$ARCHIVE_STATUS" "$ENVIRONMENT_STATUS" \
    "$BUDGET_STATUS" "$MODEL_ARTIFACT_STATUS" "$CASE" "$CASE" >> "$RUN_ROOT/run-log.md"

  [ "$ARCHIVE_STATUS" = "archived" ] || \
    fail "$CASE produced $NEW_SESSION_COUNT new session artifacts; stopped without retry"
  [ "$ENVIRONMENT_STATUS" = "verified" ] || \
    fail "$CASE session environment did not match the frozen runtime; stopped without retry"
done

printf '\nCompleted all four cases with exactly one DSH invocation per case.\n' >> "$RUN_ROOT/run-log.md"
if [ "$ANY_VALIDATION_FAILURE" -ne 0 ]; then
  printf 'Validation failed: at least one case exited nonzero, exceeded a host budget, or left unexpected workspace artifacts.\n' \
    >> "$RUN_ROOT/run-log.md"
  printf 'FAILED: %s\n' "$RUN_ROOT" >&2
  exit 1
fi
printf 'COMPLETE: %s\n' "$RUN_ROOT"
