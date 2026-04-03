"""Permission and approval policy for the marketing agent.

Permissions are runtime policy, not prompt text. The model does not decide
whether a tool is allowed — the runtime enforces it.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from .tools import TOOL_CONTRACTS


class PermissionLevel(Enum):
    AUTO_ALLOW = "auto-allow"
    ASK_FIRST = "ask-first"
    DENY = "deny"


def check_permission(tool_name: str) -> PermissionLevel:
    """Return the permission level for a tool from its contract."""
    for t in TOOL_CONTRACTS:
        if t["name"] == tool_name:
            return PermissionLevel(t["permission"])
    return PermissionLevel.DENY


def request_human_approval(tool_name: str, tool_input: dict[str, Any]) -> bool:
    """Block and ask the human operator for approval.

    In a real system this could be a Slack message, a web UI modal,
    an email, or a CLI prompt. Here we use stdin.
    """
    print(f"\n{'=' * 60}")
    print(f"APPROVAL REQUIRED: {tool_name}")
    print(f"Input: {tool_input}")
    print(f"{'=' * 60}")
    while True:
        answer = input("Approve? [y/n]: ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please enter y or n.")
