"""Meeting summary generation using Claude (Anthropic)."""

import json
import os
import textwrap
from dataclasses import dataclass
from datetime import datetime

import anthropic
from dotenv import load_dotenv

from meeting_summarizer.transcriber import Transcript


load_dotenv()

SYSTEM_PROMPT = textwrap.dedent("""\
    You are an information extraction system.

    Task:
    Analyze the following meeting transcript, which may contain English and \
    Chinese (Mandarin). Understand both languages naturally and produce a \
    structured summary in English.

    Output requirements:
    - Return exactly one valid JSON object.
    - Do not include markdown fences.
    - Do not include any explanation, notes, or text before or after the JSON.
    - Begin the response with { and end with }.
    - All keys must be present.
    - If information is missing, use:
      - null for unknown scalar values
      - [] for unknown or absent arrays
      - "Unknown" for unknown people when a person is required
      - "TBD" for unknown deadlines or due dates
    - Do not invent facts unless the task explicitly says to infer; when \
    inferring, keep it conservative.
    - Output must be in English.

    Schema:
    {
      "title": "string",
      "attendees": ["string"],
      "executive_summary": "string",
      "key_decisions": [
        {
          "decision": "string",
          "made_by": "string|null",
          "context": "string"
        }
      ],
      "action_items": [
        {
          "task": "string",
          "owner": "string",
          "deadline": "YYYY-MM-DD|TBD",
          "priority": "high|medium|low"
        }
      ],
      "discussion_topics": [
        {
          "topic": "string",
          "summary": "string",
          "outcome": "string"
        }
      ],
      "follow_ups": [
        {
          "item": "string",
          "owner": "string",
          "due_date": "YYYY-MM-DD|TBD"
        }
      ],
      "sentiment": "productive|contentious|neutral|brainstorming"
    }

    Additional extraction rules:
    - "title": infer a concise descriptive meeting title from the transcript.
    - "attendees": include speaker names, labels, or identifiers explicitly \
    mentioned or clearly detectable.
    - "executive_summary": write 2-3 sentences in English.
    - "key_decisions": include only actual decisions made, not suggestions.
    - "action_items": include concrete next steps; infer owner/deadline only \
    when strongly supported by context.
    - "discussion_topics": capture the major themes discussed.
    - "follow_ups": include unresolved items or future check-ins.
    - "sentiment": choose the single best overall tone.""")

USER_PROMPT_TEMPLATE = textwrap.dedent("""\
    Transcript:
    {transcript}""")


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

    Configure via .env (pick one):
        ANTHROPIC_API_KEY=your_key                      # direct API access
        ANTHROPIC_BASE_URL=http://127.0.0.1:3456        # Claude Max proxy (no API key needed)
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        base_url = base_url or os.getenv("ANTHROPIC_BASE_URL")
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            if base_url:
                api_key = "dummy"  # proxy ignores the key; SDK requires a non-empty value
            else:
                raise ValueError(
                    "ANTHROPIC_API_KEY is required when not using a proxy. "
                    "Set it in .env, or set ANTHROPIC_BASE_URL to use the Claude Max proxy."
                )

        kwargs: dict = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = anthropic.Anthropic(**kwargs)

    def generate_summary(self, transcript: Transcript) -> MeetingSummary:
        """Send transcript to Claude and return a structured MeetingSummary."""
        formatted = self._format_transcript(transcript)

        user_message = USER_PROMPT_TEMPLATE.format(transcript=formatted)

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        # Normalize to raw text
        raw_text = response if isinstance(response, str) else response.content[0].text

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            raise ValueError(
                f"Failed to parse JSON from Claude response: {raw_text[:200]}"
            ) from None

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
