"""External integrations (meridian, slack, etc.)."""

from meeting_summarizer.integrations.meridian import MeridianManager
from meeting_summarizer.integrations.slack import SlackNotifier

__all__ = ["MeridianManager", "SlackNotifier"]
