#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)

EXPECTED_SKILL_SHA256="5541240637eae5367ba8fbbacd180f69d7a4f1900e59efa03104acbaf7419a94"
DSH_BIN_PATH="${DSH_BIN_PATH:-/Users/xiaweiqi/.npm/_npx/1e7f6d9597241db0/node_modules/.bin/dsh}"
RESANITY_DSH_HOME="${RESANITY_DSH_HOME:-/private/tmp/resanity-v2-dsh-prelayers.swWtuP/home}"
ACTIVE_SKILL="$RESANITY_DSH_HOME/profiles/headless-resanity/node_modules/resanity/SKILL.md"

RUN_MODE="run"
if [[ "${1:-}" == "--dry-run" ]]; then
  RUN_MODE="dry-run"
  shift
fi

if [[ "$RUN_MODE" == "run" && $# -ne 1 ]]; then
  echo "usage: $0 /absolute/new/output-path" >&2
  echo "       $0 --dry-run" >&2
  exit 64
fi
if [[ "$RUN_MODE" == "dry-run" && $# -ne 0 ]]; then
  echo "usage: $0 --dry-run" >&2
  exit 64
fi
if [[ ! -x "$DSH_BIN_PATH" ]]; then
  echo "DSH binary is missing or not executable: $DSH_BIN_PATH" >&2
  exit 66
fi
if [[ ! -f "$ACTIVE_SKILL" ]]; then
  echo "active Resanity Skill is missing: $ACTIVE_SKILL" >&2
  exit 66
fi

ARGS=(
  "$REPO_ROOT/validation/v2/run_dsh_prelayers.py"
  --dsh-bin "$DSH_BIN_PATH"
  --dsh-home "$RESANITY_DSH_HOME"
  --baseline-profile headless-baseline
  --candidate-profile headless-resanity
  --active-skill "$ACTIVE_SKILL"
  --expected-provider deepseek-official
  --expected-model deepseek-v4-pro
  --expected-reasoning-effort max
  --expected-skill-sha256 "$EXPECTED_SKILL_SHA256"
  --case O02-policy-outcome
  --case O03-investing-exposure
)

if [[ "$RUN_MODE" == "run" ]]; then
  OUTPUT_ROOT="$1"
  ARGS+=(--run --output "$OUTPUT_ROOT")
fi

exec python3 "${ARGS[@]}"
