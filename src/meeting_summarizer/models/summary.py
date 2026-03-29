"""Meeting summary domain model."""

from dataclasses import dataclass


@dataclass
class MeetingSummary:
    title: str
    date: str
    duration: str
    attendees: list[str]
    executive_summary: str
    key_decisions: list[dict]
    action_items: list[dict]
    discussion_topics: list[dict]
    follow_ups: list[dict]
    raw_transcript: str
