"""Output distribution — coordinate saving and notifications."""

from meeting_summarizer.config import Settings
from meeting_summarizer.integrations.slack import SlackNotifier
from meeting_summarizer.models import MeetingSummary
from meeting_summarizer.utils.files import save_summary_json


class OutputDistributor:
    """Distribute meeting summaries to one or more destinations."""

    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or Settings()
        self._slack = SlackNotifier(settings.slack_webhook_url)

    def to_slack(self, summary: MeetingSummary) -> None:
        """Post formatted summary to Slack."""
        self._slack.post_summary(summary)

    def to_json(self, summary: MeetingSummary, output_path: str) -> None:
        """Export the full summary as a JSON file."""
        save_summary_json(summary, output_path)
