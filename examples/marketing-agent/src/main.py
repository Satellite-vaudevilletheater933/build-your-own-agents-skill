"""CLI entry point for the marketing agent."""

from __future__ import annotations

import argparse
import json
import sys

from .agent import run_agent


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Marketing agent — loop-based, tool-using, approval-gated"
    )
    parser.add_argument(
        "goal",
        nargs="?",
        default="Draft a LinkedIn post for our developer toolkit launch week.",
        help="The user goal for the agent to accomplish",
    )
    parser.add_argument(
        "--campaign",
        default="demo-001",
        help="Campaign ID (default: demo-001)",
    )
    args = parser.parse_args()

    try:
        state = run_agent(args.goal, campaign_id=args.campaign)
    except KeyboardInterrupt:
        print("\n[agent] interrupted by user")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("SESSION SUMMARY")
    print("=" * 60)
    print(json.dumps(state.summary(), indent=2))


if __name__ == "__main__":
    main()
