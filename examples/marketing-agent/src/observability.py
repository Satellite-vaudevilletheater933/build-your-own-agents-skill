"""Observability layer for the marketing agent.

Minimum viable logging: every tool call, every approval decision,
every turn, every failure. Structured JSON so it can be ingested
by any log aggregator.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(event_type: str, data: dict[str, Any], session_id: str = "") -> None:
    record = {
        "timestamp": _now(),
        "session_id": session_id,
        "event": event_type,
        **data,
    }
    print(json.dumps(record), file=sys.stderr)


def log_tool_call(
    session_id: str,
    turn: int,
    tool_name: str,
    latency_ms: float,
    success: bool,
    error: str | None = None,
) -> None:
    log_event(
        "tool_call",
        {
            "turn": turn,
            "tool": tool_name,
            "latency_ms": round(latency_ms, 2),
            "success": success,
            "error": error,
        },
        session_id=session_id,
    )


def log_approval(
    session_id: str, turn: int, tool_name: str, approved: bool
) -> None:
    log_event(
        "approval_decision",
        {"turn": turn, "tool": tool_name, "approved": approved},
        session_id=session_id,
    )


def log_turn(
    session_id: str,
    turn: int,
    input_tokens: int,
    output_tokens: int,
) -> None:
    log_event(
        "turn_complete",
        {
            "turn": turn,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        },
        session_id=session_id,
    )


def log_session_end(session_id: str, summary: dict[str, Any]) -> None:
    log_event("session_end", summary, session_id=session_id)
