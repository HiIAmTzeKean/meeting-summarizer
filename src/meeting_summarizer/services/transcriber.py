"""Audio transcription using OpenAI Whisper (runs fully locally)."""

import subprocess
import tempfile
from pathlib import Path

import whisper

from meeting_summarizer.config import Settings
from meeting_summarizer.models import Transcript, TranscriptSegment


class AudioTranscriber:
    """Transcribe audio files locally using Whisper.

    Model is loaded from ~/.cache/whisper/ after the first download.
    Supports multilingual audio (English, Chinese, etc.).
    """

    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or Settings()
        model_size = settings.whisper_model
        print(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        self.language = settings.meeting_language

    def transcribe_file(self, audio_path: str) -> Transcript:
        """Transcribe an audio file and return structured segments."""
        kwargs: dict = {
            "verbose": False,
            "word_timestamps": True,
            "condition_on_previous_text": True,
        }

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
