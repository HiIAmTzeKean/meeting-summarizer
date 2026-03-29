"""Thin CLI entrypoint — parse args, build settings, run pipeline."""

import argparse

from meeting_summarizer.pipeline.meeting_pipeline import process_meeting


def cli() -> None:
    """CLI entrypoint registered in pyproject.toml."""
    parser = argparse.ArgumentParser(
        prog="meeting-summarizer",
        description=(
            "Transcribe and summarize meeting audio using Whisper + Claude.\n"
            "Supports English and Chinese (Mandarin). Configure via .env file."
        ),
    )
    parser.add_argument("audio_path", help="Path to the meeting audio file (wav, mp3, m4a, etc.)")
    args = parser.parse_args()
    process_meeting(args.audio_path)


if __name__ == "__main__":
    cli()
