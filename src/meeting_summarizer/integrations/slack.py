"""Slack integration — post meeting summaries via webhook."""

import requests

from meeting_summarizer.models import MeetingSummary


class SlackNotifier:
    """Post formatted meeting summaries to a Slack channel."""

    def __init__(self, webhook_url: str | None) -> None:
        self.webhook_url = webhook_url

    def post_summary(self, summary: MeetingSummary) -> None:
        """Post formatted summary to Slack. No-ops if webhook is not configured."""
        if not self.webhook_url:
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

        resp = requests.post(self.webhook_url, json={"blocks": blocks}, timeout=10)
        print(f"Slack response: {resp.status_code}")
