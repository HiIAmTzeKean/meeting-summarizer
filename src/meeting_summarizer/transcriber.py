"""Audio transcription using OpenAI Whisper (runs fully locally)."""

import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import whisper
from dotenv import load_dotenv


load_dotenv()


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


class AudioTranscriber:
    """Transcribe audio files locally using Whisper.

    Model is loaded from ~/.cache/whisper/ after the first download.
    Supports multilingual audio (English, Chinese, etc.).

    Configure via .env:
        WHISPER_MODEL=medium       # tiny | base | small | medium | large
        MEETING_LANGUAGE=auto      # auto | en | zh | ...
    """

    def __init__(self, model_size: str | None = None) -> None:
        model_size = model_size or os.getenv("WHISPER_MODEL", "medium")
        print(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        self.language = os.getenv("MEETING_LANGUAGE", "auto")

    def transcribe_file(self, audio_path: str) -> Transcript:
        """Transcribe an audio file and return structured segments.

        Set MEETING_LANGUAGE=auto to let Whisper detect per segment,
        which works best for mixed English/Chinese conversations.
        """
        kwargs: dict = dict(
            verbose=False,
            word_timestamps=True,
            condition_on_previous_text=True,
        )

        if self.language and self.language.lower() != "auto":
            lang = self.language.split(",")[0].strip()
            kwargs["language"] = lang

        result = self.model.transcribe(audio_path, **kwargs)

        segments = [
            TranscriptSegment(
                start=seg["start"],
                end=seg["end"],
                text=seg["text"].strip(),
            )
            for seg in result["segments"]
        ]

        return Transcript(
            segments=segments,
            full_text=result["text"].strip(),
            duration_seconds=segments[-1].end if segments else 0,
            language=result.get("language", self.language),
        )

    def transcribe_from_system_audio(self, duration_seconds: int) -> Transcript:
        """Record system audio (macOS via sox) and transcribe."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name

        subprocess.run(
            ["sox", "-d", "-r", "16000", "-c", "1", tmp_path, "trim", "0", str(duration_seconds)],
            check=True,
        )

        transcript = self.transcribe_file(tmp_path)
        Path(tmp_path).unlink()
        return transcript
