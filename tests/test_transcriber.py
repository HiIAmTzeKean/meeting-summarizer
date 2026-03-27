"""Basic unit tests for the transcriber module."""

from meeting_summarizer.transcriber import Transcript, TranscriptSegment


def test_transcript_segment_defaults():
    seg = TranscriptSegment(start=0.0, end=5.0, text="Hello")
    assert seg.speaker is None
    assert seg.text == "Hello"


def test_transcript_duration():
    segments = [
        TranscriptSegment(start=0.0, end=10.0, text="First"),
        TranscriptSegment(start=10.0, end=30.0, text="Second"),
    ]
    transcript = Transcript(
        segments=segments,
        full_text="First Second",
        duration_seconds=30.0,
        language="en",
    )
    assert transcript.duration_seconds == 30.0
    assert len(transcript.segments) == 2
