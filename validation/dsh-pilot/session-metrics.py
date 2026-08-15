#!/usr/bin/env python3
"""Extract non-semantic run metrics from one DSH JSONL session artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import IO, Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract counts, IDs, timestamps, and runtime config without message text."
    )
    parser.add_argument(
        "--format",
        choices=("metrics", "host-receipt"),
        default="metrics",
        help="emit diagnostic metrics or a normalized host-owned receipt",
    )
    parser.add_argument("session", type=Path, help="session.jsonl or session.jsonl.zstd")
    return parser.parse_args()


def open_session(path: Path) -> tuple[IO[str], subprocess.Popen[str] | None]:
    if path.name.endswith(".zstd"):
        process = subprocess.Popen(
            ["zstd", "-dc", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if process.stdout is None:
            raise RuntimeError("zstd stdout pipe was not created")
        return process.stdout, process
    return path.open("r", encoding="utf-8"), None


def integer(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    path: Path = args.session
    if not path.is_file():
        print(f"session artifact does not exist: {path}", file=sys.stderr)
        return 2
    if path.name not in {"session.jsonl", "session.jsonl.zstd", "raw-session.jsonl", "raw-session.jsonl.zstd"}:
        print(f"unsupported session artifact name: {path.name}", file=sys.stderr)
        return 2

    event_types: Counter[str] = Counter()
    tool_calls: Counter[str] = Counter()
    session_id = None
    session_cwd = None
    created_at_ms = None
    provider = None
    model = None
    reasoning_effort = None
    permission_preset = None
    sandbox_mode = None
    approval_policy = None
    available_tools: list[str] = []
    first_ms = None
    last_ms = None
    input_tokens = 0
    output_tokens = 0
    reasoning_tokens = 0
    cache_read_tokens = 0
    malformed_lines = 0

    stream, process = open_session(path)
    try:
        for raw_line in stream:
            line = raw_line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                malformed_lines += 1
                continue
            if not isinstance(event, dict):
                malformed_lines += 1
                continue

            event_type = event.get("type")
            if not isinstance(event_type, str):
                event_type = "?"
            event_types[event_type] += 1

            timestamp = event.get("time")
            if isinstance(timestamp, int) and not isinstance(timestamp, bool):
                first_ms = timestamp if first_ms is None else min(first_ms, timestamp)
                last_ms = timestamp if last_ms is None else max(last_ms, timestamp)

            data = event.get("data")
            if not isinstance(data, dict):
                data = {}

            if event_type == "session":
                session_id = event.get("id")
                session_cwd = event.get("cwd")
                created_at_ms = event.get("createdAt")
            elif event_type == "permission/preset":
                permission_preset = data.get("preset")
            elif event_type == "sandbox/mode":
                sandbox_mode = data.get("mode")
            elif event_type == "approval/policy":
                approval_policy = data.get("policy")
            elif event_type == "request/header":
                header = data.get("header")
                if isinstance(header, dict):
                    config = header.get("config")
                    if isinstance(config, dict):
                        provider = provider or config.get("provider")
                        model = model or config.get("model")
                        reasoning_effort = reasoning_effort or config.get("reasoningEffort")
                    tools = header.get("tools")
                    if isinstance(tools, list):
                        available_tools = sorted(
                            {
                                item.get("name")
                                for item in tools
                                if isinstance(item, dict) and isinstance(item.get("name"), str)
                            }
                        )
            elif event_type == "tool/call":
                name = data.get("name")
                tool_calls[name if isinstance(name, str) else "?"] += 1

            usage = data.get("usage")
            if isinstance(usage, dict):
                input_tokens += integer(usage.get("inputTokens"))
                output_tokens += integer(usage.get("outputTokens"))
                reasoning_tokens += integer(usage.get("reasoningTokens"))
                cache_read_tokens += integer(usage.get("cacheReadTokens"))

            message = data.get("message")
            if isinstance(message, dict):
                source = message.get("source")
                if isinstance(source, dict):
                    provider = provider or source.get("provider")
                    model = model or source.get("model")
    finally:
        stream.close()

    if process is not None:
        stderr = process.stderr.read() if process.stderr is not None else ""
        return_code = process.wait()
        if return_code != 0:
            print(f"zstd failed with exit {return_code}: {stderr.strip()}", file=sys.stderr)
            return 3

    metrics = {
        "schema": "resanity.dsh-session-metrics.v1",
        "session_id": session_id,
        "session_cwd": session_cwd,
        "created_at_ms": created_at_ms,
        "provider": provider,
        "model": model,
        "reasoning_effort": reasoning_effort,
        "permission_preset": permission_preset,
        "sandbox_mode": sandbox_mode,
        "approval_policy": approval_policy,
        "available_tools": available_tools,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "reasoning_tokens": reasoning_tokens,
        "cache_read_tokens": cache_read_tokens,
        "steps": event_types["step/start"],
        "tool_calls": sum(tool_calls.values()),
        "tool_results": event_types["tool/result"],
        "tool_calls_by_name": dict(sorted(tool_calls.items())),
        "skill_tool_calls": tool_calls["skill"],
        "web_search_tool_calls": tool_calls["web_search"],
        "web_search_llm_requests": event_types["web/deepseek-search-llm-request"],
        "first_ms": first_ms,
        "last_ms": last_ms,
        "wall_ms": last_ms - first_ms if first_ms is not None and last_ms is not None else None,
        "malformed_lines": malformed_lines,
        "event_types": dict(sorted(event_types.items())),
    }
    result: dict[str, Any] = metrics
    if args.format == "host-receipt":
        wall_ms = metrics["wall_ms"]
        wall_seconds = math.ceil(wall_ms / 1000) if isinstance(wall_ms, int) else None
        tokens_total = input_tokens + output_tokens + reasoning_tokens
        result = {
            "schema_version": "resanity.host-receipt.v1",
            "host": "dsh",
            "provider": provider,
            "model": model,
            "session_id": session_id,
            "runtime": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "reasoning_tokens": reasoning_tokens,
                "cache_read_tokens": cache_read_tokens,
                "tokens_total": tokens_total,
                "tool_calls": metrics["tool_calls"],
                "wall_seconds": wall_seconds,
            },
            "budget_usage": {
                "tokens_total": tokens_total,
                "tool_calls": metrics["tool_calls"],
                "web_search": metrics["web_search_tool_calls"],
                "wall_seconds": wall_seconds,
            },
            "tool_calls_by_name": metrics["tool_calls_by_name"],
            "raw_session": {
                "path": path.name,
                "sha256": sha256_file(path),
            },
            "extractor": {
                "path": Path(__file__).name,
                "sha256": sha256_file(Path(__file__)),
            },
        }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
