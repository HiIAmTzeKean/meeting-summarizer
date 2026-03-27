"""Output distribution — push summaries to Slack, JSON, etc."""

import dataclasses
import json
import os

import requests
from dotenv import load_dotenv

from meeting_summarizer.summary_engine import MeetingSummary

load_dotenv()


class OutputDistributor:
    """Distribute meeting summaries to one or more destinations.

    Configure via .env:
        SLACK_WEBHOOK_URL=https://hooks.slack.com/...   (optional)
        NOTION_TOKEN=...                                 (optional)
        NOTION_DATABASE_ID=...                           (optional)
    """

    def __init__(self, config: dict | None = None) -> None:
        config = config or {}
        self.slack_webhook = config.get("slack_webhook") or os.getenv("SLACK_WEBHOOK_URL")
        self.notion_token = config.get("notion_token") or os.getenv("NOTION_TOKEN")
        self.notion_db = config.get("notion_database_id") or os.getenv("NOTION_DATABASE_ID")

    def to_slack(self, summary: MeetingSummary) -> None:
        """Post formatted summary to a Slack channel via webhook."""
        if not self.slack_webhook:
            print("Skipping Slack: SLACK_WEBHOOK_URL not set in .env")
            return

        action_list = "\n".join(
            f" - [ ] {a['task']} -> *{a['owner']}* (due: {a.get('deadline', 'TBD')})"
            for a in summary.action_items
        )
        decision_list = "\n".join(f" - {d['decision']}" for d in summary.key_decisions)

        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": summary.title}},
            {"type": "section", "text": {"type": "mrkdwn", "text": summary.executive_summary}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Decisions:*\n{decision_list}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Action Items:*\n{action_list}"}},
        ]

        resp = requests.post(self.slack_webhook, json={"blocks": blocks}, timeout=10)
        print(f"Slack response: {resp.status_code}")

    def to_json(self, summary: MeetingSummary, output_path: str) -> None:
        """Export the full summary as a JSON file (preserves CJK characters)."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dataclasses.asdict(summary), f, indent=2, ensure_ascii=False)
        print(f"Saved: {output_path}")
