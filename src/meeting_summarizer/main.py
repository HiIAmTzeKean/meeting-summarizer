"""CLI entry point for the meeting summarizer pipeline."""

import argparse

from dotenv import load_dotenv

from meeting_summarizer.transcriber import AudioTranscriber
from meeting_summarizer.diarizer import SpeakerDiarizer
from meeting_summarizer.summary_engine import SummaryEngine
from meeting_summarizer.distributor import OutputDistributor

load_dotenv()


def process_meeting(audio_path: str) -> None:
    """Run the full pipeline: transcribe → diarize → summarize → distribute."""

    # 1. Transcribe (local Whisper — no audio leaves machine)
    transcriber = AudioTranscriber()
    transcript = transcriber.transcribe_file(audio_path)
    print(f"Transcribed {transcript.duration_seconds:.0f}s of audio (language: {transcript.language})")

    # 2. Identify speakers
    diarizer = SpeakerDiarizer()
    transcript = diarizer.assign_speakers(audio_path, transcript)
    speakers = {s.speaker for s in transcript.segments if s.speaker}
    print(f"Identified {len(speakers)} speakers: {', '.join(speakers)}")

    # 3. Generate structured summary
    engine = SummaryEngine()
    summary = engine.generate_summary(transcript)
    print(f"Generated summary: {summary.title}")

    # 4. Distribute
    distributor = OutputDistributor()
    distributor.to_slack(summary)
    output_file = f"meeting_{summary.date}.json"
    distributor.to_json(summary, output_file)

    # 5. Print to console
    sep = "=" * 52
    print(f"\n{sep}")
    print(f"Title    : {summary.title}")
    print(f"Date     : {summary.date}")
    print(f"Duration : {summary.duration}")
    print(f"Attendees: {', '.join(summary.attendees)}")
    print(f"\nExecutive Summary:\n{summary.executive_summary}")

    if summary.key_decisions:
        print("\nKey Decisions:")
        for d in summary.key_decisions:
            print(f"  • {d['decision']}")

    if summary.action_items:
        print("\nAction Items:")
        for a in summary.action_items:
            print(f"  [{a.get('priority', '?').upper()}] {a['task']} → {a['owner']} (due: {a.get('deadline', 'TBD')})")

    if summary.follow_ups:
        print("\nFollow-ups:")
        for fu in summary.follow_ups:
            print(f"  • {fu['item']} → {fu['owner']} (by {fu.get('due_date', 'TBD')})")

    print(f"\nFull summary saved to: {output_file}")


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
