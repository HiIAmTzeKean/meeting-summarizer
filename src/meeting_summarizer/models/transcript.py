"""Transcript domain models."""

from dataclasses import dataclass


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str
    speaker: str | None = None


@dataclass
class Transcript:
    segments: list[TranscriptSegment]
    full_text: str
    duration_seconds: float
    language: str
