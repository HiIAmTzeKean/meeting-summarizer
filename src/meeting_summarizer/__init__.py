"""Meeting Summarizer — transcribe, diarize, and summarize meetings with Whisper + Claude."""

__version__ = "0.1.0"

from meeting_summarizer.models import MeetingSummary, Transcript, TranscriptSegment

__all__ = ["MeetingSummary", "Transcript", "TranscriptSegment"]
