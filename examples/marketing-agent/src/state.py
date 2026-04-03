"""Session state for the marketing agent."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ApprovalState(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


@dataclass
class ToolCall:
    tool_name: str
    input_data: dict[str, Any]
    output_data: dict[str, Any] | None = None
    error: str | None = None
    latency_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Draft:
    content: str
    channel: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    approval: ApprovalState = ApprovalState.PENDING


@dataclass
class SessionState:
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    campaign_id: str = ""
    objective: str = ""
    drafts: list[Draft] = field(default_factory=list)
    approval_state: ApprovalState = ApprovalState.PENDING
    published_posts: list[dict[str, Any]] = field(default_factory=list)
    analytics_snapshots: list[dict[str, Any]] = field(default_factory=list)
    tool_history: list[ToolCall] = field(default_factory=list)
    turn_count: int = 0
    retry_budget: int = 3
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    completed: bool = False
    failure_reason: str | None = None

    def record_tool_call(self, call: ToolCall) -> None:
        self.tool_history.append(call)

    def summary(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "campaign_id": self.campaign_id,
            "turns": self.turn_count,
            "drafts": len(self.drafts),
            "published": len(self.published_posts),
            "approval_state": self.approval_state.value,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "tool_calls": len(self.tool_history),
            "completed": self.completed,
        }
