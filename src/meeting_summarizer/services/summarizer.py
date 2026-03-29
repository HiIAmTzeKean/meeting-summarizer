"""Meeting summary generation — glues LLM client, prompts, and parsing."""

import json
from datetime import datetime

from meeting_summarizer.config import Settings
from meeting_summarizer.llm import AnthropicClient, extract_text_block, parse_llm_json
from meeting_summarizer.models import MeetingSummary, Transcript
from meeting_summarizer.prompts import SYSTEM_PROMPT, build_summary_prompt
from meeting_summarizer.utils.time import fmt_time


class SummaryEngine:
    """Generate structured meeting summaries using Claude.

    Handles bilingual transcripts (English + Chinese).
    Summary output is always in English.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.client = AnthropicClient(settings)

    def generate_summary(self, transcript: Transcript) -> MeetingSummary:
        """Send transcript to Claude and return a structured MeetingSummary."""
        formatted = self._format_transcript(transcript)
        user_message = build_summary_prompt(formatted)

        response = self.client.stream_message(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        raw_text = extract_text_block(response)

        try:
            data = parse_llm_json(raw_text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Failed to parse JSON from Claude response "
                f"(stop_reason={response.stop_reason}, len={len(raw_text)}).\n"
                f"Parse error: {exc}\n"
                f"First 500 chars: {raw_text[:500]}\n"
                f"Last 200 chars: {raw_text[-200:]}"
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
            timestamp = f"[{fmt_time(seg.start)}]"
            speaker = seg.speaker or "Speaker"
            lines.append(f"{timestamp} {speaker}: {seg.text}")
        return "\n".join(lines)
