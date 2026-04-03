"""Marketing agent controller loop.

This is the core runtime: it builds context, calls the model, checks
permissions, executes tools, updates state, and loops until a stop
condition is reached.

Architecture:
  User goal -> context builder -> model turn -> tool decision
  -> permission check -> tool executor -> state update -> loop
"""

from __future__ import annotations

import json
import os
from typing import Any

import anthropic

from . import observability as obs
from .permissions import PermissionLevel, check_permission, request_human_approval
from .state import ApprovalState, Draft, SessionState, ToolCall
from .tools import TOOL_CONTRACTS, _anthropic_tools, execute_tool

MAX_TURNS = 20
DEFAULT_MODEL = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = """\
You are a marketing operations agent. You help teams discover topics, \
draft posts, get approval, publish content, and track performance.

Rules:
- Always fetch the campaign brief before drafting.
- Draft at least one post before requesting to publish.
- Never publish without the user approving first.
- After publishing, fetch metrics if the user asks for them.
- If you have completed the user's request, respond with a final summary \
and do not request any more tools.

Available tools: {tool_names}

Current session state:
{state_summary}
"""


def _build_system_prompt(state: SessionState) -> str:
    tool_names = ", ".join(t["name"] for t in TOOL_CONTRACTS)
    return SYSTEM_PROMPT.format(
        tool_names=tool_names,
        state_summary=json.dumps(state.summary(), indent=2),
    )


def run_agent(user_goal: str, campaign_id: str = "demo-001") -> SessionState:
    """Run the marketing agent loop to completion.

    Returns the final session state.
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    state = SessionState(campaign_id=campaign_id, objective=user_goal)
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_goal}]

    print(f"[agent] session={state.session_id} goal={user_goal!r}")

    for turn in range(1, MAX_TURNS + 1):
        state.turn_count = turn
        system = _build_system_prompt(state)

        response = client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL),
            max_tokens=4096,
            system=system,
            tools=_anthropic_tools(),
            messages=messages,
        )

        state.total_input_tokens += response.usage.input_tokens
        state.total_output_tokens += response.usage.output_tokens
        obs.log_turn(
            state.session_id, turn,
            response.usage.input_tokens, response.usage.output_tokens,
        )

        assistant_content = response.content
        messages.append({"role": "assistant", "content": assistant_content})

        tool_use_blocks = [b for b in assistant_content if b.type == "tool_use"]

        # --- Stop condition: model finished without requesting tools ---
        if not tool_use_blocks:
            text_parts = [b.text for b in assistant_content if hasattr(b, "text")]
            print(f"[agent] final response:\n{''.join(text_parts)}")
            state.completed = True
            break

        # --- Process each tool call ---
        tool_results: list[dict[str, Any]] = []
        for block in tool_use_blocks:
            tool_name = block.name
            tool_input = block.input
            raw_input = json.dumps(tool_input)

            # Permission check (runtime policy, not prompt)
            perm = check_permission(tool_name)

            if perm == PermissionLevel.DENY:
                obs.log_tool_call(state.session_id, turn, tool_name, 0, False, "denied")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps({"error": "Tool denied by policy"}),
                    "is_error": True,
                })
                continue

            if perm == PermissionLevel.ASK_FIRST:
                approved = request_human_approval(tool_name, tool_input)
                obs.log_approval(state.session_id, turn, tool_name, approved)
                if not approved:
                    state.approval_state = ApprovalState.DENIED
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps({"error": "Human denied approval"}),
                        "is_error": True,
                    })
                    continue
                state.approval_state = ApprovalState.APPROVED

            # Execute tool
            try:
                result_json, latency = execute_tool(tool_name, raw_input)
                obs.log_tool_call(state.session_id, turn, tool_name, latency, True)

                call = ToolCall(
                    tool_name=tool_name,
                    input_data=tool_input,
                    output_data=json.loads(result_json),
                    latency_ms=latency,
                )
                state.record_tool_call(call)

                # Update domain-specific state
                if tool_name == "draft_post":
                    result_data = json.loads(result_json)
                    state.drafts.append(Draft(
                        content=result_data.get("draft", ""),
                        channel=result_data.get("channel", ""),
                    ))
                elif tool_name == "publish_post":
                    state.published_posts.append(json.loads(result_json))
                elif tool_name == "fetch_post_metrics":
                    state.analytics_snapshots.append(json.loads(result_json))

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_json,
                })

            except Exception as exc:
                error_msg = str(exc)
                obs.log_tool_call(state.session_id, turn, tool_name, 0, False, error_msg)

                state.retry_budget -= 1
                call = ToolCall(
                    tool_name=tool_name,
                    input_data=tool_input,
                    error=error_msg,
                )
                state.record_tool_call(call)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps({"error": error_msg}),
                    "is_error": True,
                })

                # Stop condition: retry budget exhausted
                if state.retry_budget <= 0:
                    state.failure_reason = "Retry budget exhausted"
                    state.completed = True
                    break

        messages.append({"role": "user", "content": tool_results})

        # Stop condition: approval denied
        if state.approval_state == ApprovalState.DENIED:
            state.failure_reason = "Approval denied"
            state.completed = True
            break

    else:
        state.failure_reason = f"Reached maximum turns ({MAX_TURNS})"
        state.completed = True

    obs.log_session_end(state.session_id, state.summary())
    return state
