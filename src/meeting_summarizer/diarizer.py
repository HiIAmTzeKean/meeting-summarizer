"""Speaker diarization using pyannote.audio."""

import os

import torch
from dotenv import load_dotenv
from pyannote.audio import Pipeline

from meeting_summarizer.transcriber import Transcript


load_dotenv()


class SpeakerDiarizer:
    """Identify and label speakers in a transcript using pyannote.

    Requires a HuggingFace token with access to:
    https://huggingface.co/pyannote/speaker-diarization-3.1

    Configure via .env:
        HF_TOKEN=your_huggingface_token
    """

    def __init__(self, hf_token: str | None = None) -> None:
        hf_token = hf_token or os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN is required for speaker diarization. Set it in .env")

        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=hf_token,
        )
        if self.pipeline is None:
            raise RuntimeError("Failed to load pyannote speaker diarization pipeline. Check your HF_TOKEN and model access.")
        if torch.cuda.is_available():
            self.pipeline.to(torch.device("cuda"))

    def assign_speakers(self, audio_path: str, transcript: Transcript) -> Transcript:
        """Run diarization and assign speaker labels to each segment."""
        result = self.pipeline(audio_path)
        diarization = result.speaker_diarization if hasattr(result, "speaker_diarization") else result

        for segment in transcript.segments:
            mid_time = (segment.start + segment.end) / 2
            segment.speaker = self._get_speaker_at_time(diarization, mid_time)

        return transcript

    def _get_speaker_at_time(self, diarization: object, time: float) -> str:
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            if turn.start <= time <= turn.end:
                return speaker
        return "UNKNOWN"
