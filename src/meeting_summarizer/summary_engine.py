"""Meeting summary generation using Claude (Anthropic)."""

import json
import os
from dataclasses import dataclass
from datetime import datetime

import anthropic
from dotenv import load_dotenv

from meeting_summarizer.transcriber import Transcript

load_dotenv()


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


class SummaryEngine:
    """Generate structured meeting summaries using Claude.

    Handles bilingual transcripts (English + Chinese).
    Summary output is always in English.

    Configure via .env:
        ANTHROPIC_API_KEY=your_key
    """

    def __init__(self, api_key: str | None = None) -> None:
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required. Set it in .env")
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_summary(self, transcript: Transcript) -> MeetingSummary:
        """Send transcript to Claude and return a structured MeetingSummary."""
        formatted = self._format_transcript(transcript)

        prompt = f"""You are analyzing a meeting transcript that may contain a mix of English and Chinese (Mandarin).
Understand both languages naturally and produce the summary in English.

Analyze this meeting transcript and extract a structured summary.

Return a JSON object with these fields:
- title: A descriptive meeting title (infer from content)
- attendees: List of speaker identifiers mentioned or detected
- executive_summary: 2-3 sentence high-level summary in English
- key_decisions: Array of objects with "decision", "made_by", "context"
- action_items: Array of objects with "task", "owner", "deadline" (infer if not stated), "priority" (high/medium/low)
- discussion_topics: Array of objects with "topic", "summary", "outcome"
- follow_ups: Array of objects with "item", "owner", "due_date"
- sentiment: Overall meeting tone (productive/contentious/neutral/brainstorming)

Transcript:
{formatted}

Return ONLY valid JSON."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        data = json.loads(response.content[0].text)
        duration_min = int(transcript.duration_seconds / 60)

        return MeetingSummary(
            title=data["title"],
            date=datetime.now().strftime("%Y-%m-%d"),
            duration=f"{duration_min} minutes",
            attendees=data["attendees"],
            executive_summary=data["executive_summary"],
            key_decisions=data["key_decisions"],
            action_items=data["action_items"],
            discussion_topics=data["discussion_topics"],
            follow_ups=data["follow_ups"],
            raw_transcript=formatted,
        )

    def _format_transcript(self, transcript: Transcript) -> str:
        lines = []
        for seg in transcript.segments:
            timestamp = f"[{self._fmt_time(seg.start)}]"
            speaker = seg.speaker or "Speaker"
            lines.append(f"{timestamp} {speaker}: {seg.text}")
        return "\n".join(lines)

    @staticmethod
    def _fmt_time(seconds: float) -> str:
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
