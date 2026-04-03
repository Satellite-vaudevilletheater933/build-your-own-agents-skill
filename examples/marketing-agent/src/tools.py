"""Tool definitions and executor for the marketing agent.

Each tool is defined as a contract (schema) and an executor (implementation).
The model sees the contracts. The runtime calls the executors.
"""

from __future__ import annotations

import json
import time
from typing import Any

TOOL_CONTRACTS: list[dict[str, Any]] = [
    {
        "name": "get_trending_topics",
        "description": "Fetch recent high-signal topics for a target audience and channel. Returns a list of topic strings with relevance scores.",
        "input_schema": {
            "type": "object",
            "properties": {
                "audience": {
                    "type": "string",
                    "description": "Target audience segment",
                },
                "channel": {
                    "type": "string",
                    "enum": ["twitter", "linkedin", "blog"],
                    "description": "Social channel to find trends for",
                },
            },
            "required": ["audience", "channel"],
        },
        "permission": "auto-allow",
        "timeout_seconds": 15,
        "side_effects": "none",
    },
    {
        "name": "get_campaign_brief",
        "description": "Retrieve the campaign brief for the current campaign ID. Returns objectives, constraints, tone, and key messages.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {
                    "type": "string",
                    "description": "The campaign identifier",
                },
            },
            "required": ["campaign_id"],
        },
        "permission": "auto-allow",
        "timeout_seconds": 10,
        "side_effects": "none",
    },
    {
        "name": "get_brand_guide",
        "description": "Retrieve the brand voice guide for the current campaign. Returns tone rules, forbidden phrases, and style constraints.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {
                    "type": "string",
                    "description": "The campaign identifier",
                },
            },
            "required": ["campaign_id"],
        },
        "permission": "auto-allow",
        "timeout_seconds": 10,
        "side_effects": "none",
    },
    {
        "name": "draft_post",
        "description": "Generate a draft social media post. Returns the draft text and metadata. Does NOT publish.",
        "input_schema": {
            "type": "object",
            "properties": {
                "channel": {
                    "type": "string",
                    "enum": ["twitter", "linkedin", "blog"],
                },
                "topic": {"type": "string", "description": "Topic to write about"},
                "tone": {"type": "string", "description": "Desired tone (professional, casual, etc.)"},
                "key_messages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key points to include",
                },
            },
            "required": ["channel", "topic"],
        },
        "permission": "auto-allow",
        "timeout_seconds": 30,
        "side_effects": "none",
    },
    {
        "name": "publish_post",
        "description": "Publish an approved post to a social channel. This is a destructive action that requires human approval.",
        "input_schema": {
            "type": "object",
            "properties": {
                "channel": {
                    "type": "string",
                    "enum": ["twitter", "linkedin", "blog"],
                },
                "content": {"type": "string", "description": "Post content to publish"},
                "draft_index": {
                    "type": "integer",
                    "description": "Index of the approved draft",
                },
            },
            "required": ["channel", "content"],
        },
        "permission": "ask-first",
        "timeout_seconds": 20,
        "side_effects": "publishes content to external platform",
    },
    {
        "name": "fetch_post_metrics",
        "description": "Fetch engagement metrics for a published post. Returns impressions, clicks, likes, shares.",
        "input_schema": {
            "type": "object",
            "properties": {
                "post_id": {"type": "string", "description": "ID of the published post"},
            },
            "required": ["post_id"],
        },
        "permission": "auto-allow",
        "timeout_seconds": 15,
        "side_effects": "none",
    },
]


def _anthropic_tools() -> list[dict[str, Any]]:
    """Convert tool contracts into the Anthropic API tool format."""
    return [
        {
            "name": t["name"],
            "description": t["description"],
            "input_schema": t["input_schema"],
        }
        for t in TOOL_CONTRACTS
    ]


def _permission_for(tool_name: str) -> str:
    for t in TOOL_CONTRACTS:
        if t["name"] == tool_name:
            return t["permission"]
    return "deny"


# ---------------------------------------------------------------------------
# Tool executors (mock implementations — swap these for real integrations)
# ---------------------------------------------------------------------------


def _exec_get_trending_topics(inp: dict[str, Any]) -> dict[str, Any]:
    """Simulated trending topics fetch."""
    return {
        "topics": [
            {"topic": "AI agents in production", "relevance": 0.92},
            {"topic": "Developer productivity tools", "relevance": 0.87},
            {"topic": "Open source AI frameworks", "relevance": 0.81},
        ],
        "channel": inp.get("channel", "unknown"),
    }


def _exec_get_campaign_brief(inp: dict[str, Any]) -> dict[str, Any]:
    return {
        "campaign_id": inp.get("campaign_id", "demo-001"),
        "objective": "Increase developer awareness of our agent toolkit",
        "tone": "professional but approachable",
        "key_messages": [
            "Build agents, not chatbots",
            "Production-ready from day one",
            "Open source and extensible",
        ],
        "constraints": ["No competitor mentions", "Under 280 chars for Twitter"],
    }


def _exec_get_brand_guide(inp: dict[str, Any]) -> dict[str, Any]:
    return {
        "campaign_id": inp.get("campaign_id", "demo-001"),
        "tone": "professional but approachable",
        "voice_attributes": ["clear", "confident", "helpful"],
        "forbidden_phrases": ["synergy", "disrupt", "leverage"],
        "style_constraints": [
            "Use active voice",
            "No jargon without explanation",
            "Keep sentences under 25 words when possible",
        ],
    }


def _exec_draft_post(inp: dict[str, Any]) -> dict[str, Any]:
    topic = inp.get("topic", "AI agents")
    channel = inp.get("channel", "twitter")
    tone = inp.get("tone", "professional")
    draft = f"[{channel.upper()} DRAFT] {topic} — built for production, not just demos. "
    if channel == "twitter":
        draft = draft[:270] + "..."
    return {"draft": draft, "channel": channel, "tone": tone, "char_count": len(draft)}


def _exec_publish_post(inp: dict[str, Any]) -> dict[str, Any]:
    return {
        "post_id": f"post-{int(time.time())}",
        "channel": inp.get("channel", "unknown"),
        "published": True,
        "content_preview": inp.get("content", "")[:80],
    }


def _exec_fetch_post_metrics(inp: dict[str, Any]) -> dict[str, Any]:
    return {
        "post_id": inp.get("post_id", "unknown"),
        "impressions": 1420,
        "clicks": 87,
        "likes": 34,
        "shares": 12,
    }


_EXECUTORS = {
    "get_trending_topics": _exec_get_trending_topics,
    "get_campaign_brief": _exec_get_campaign_brief,
    "get_brand_guide": _exec_get_brand_guide,
    "draft_post": _exec_draft_post,
    "publish_post": _exec_publish_post,
    "fetch_post_metrics": _exec_fetch_post_metrics,
}


def execute_tool(tool_name: str, raw_input: str) -> tuple[str, float]:
    """Run a tool by name. Returns (json_result, latency_ms).

    Raises ValueError for unknown tools.
    """
    executor = _EXECUTORS.get(tool_name)
    if executor is None:
        raise ValueError(f"Unknown tool: {tool_name}")
    inp = json.loads(raw_input) if isinstance(raw_input, str) else raw_input
    start = time.monotonic()
    result = executor(inp)
    latency = (time.monotonic() - start) * 1000
    return json.dumps(result), latency
