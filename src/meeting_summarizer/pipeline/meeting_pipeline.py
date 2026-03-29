"""Orchestration layer — runs the full meeting summarizer pipeline."""

from datetime import datetime
from pathlib import Path

from meeting_summarizer.config import Settings
from meeting_summarizer.integrations.meridian import MeridianManager
from meeting_summarizer.models import MeetingSummary
from meeting_summarizer.services.diarizer import SpeakerDiarizer
from meeting_summarizer.services.distributor import OutputDistributor
from meeting_summarizer.services.summarizer import SummaryEngine
from meeting_summarizer.services.transcriber import AudioTranscriber
from meeting_summarizer.utils.text import slugify


def process_meeting(audio_path: str, settings: Settings | None = None) -> MeetingSummary:
    """Run the full pipeline: transcribe -> diarize -> summarize -> distribute."""
    settings = settings or Settings()

    # 1. Transcribe (local Whisper — no audio leaves machine)
    transcriber = AudioTranscriber(settings)
    transcript = transcriber.transcribe_file(audio_path)
    print(f"Transcribed {transcript.duration_seconds:.0f}s of audio (language: {transcript.language})")

    # 2. Identify speakers
    diarizer = SpeakerDiarizer(settings)
    transcript = diarizer.assign_speakers(audio_path, transcript)
    speakers = {s.speaker for s in transcript.segments if s.speaker}
    print(f"Identified {len(speakers)} speakers: {', '.join(speakers)}")

    # 3. Generate structured summary (launch meridian proxy first)
    meridian = MeridianManager(settings.meridian_startup_timeout)
    with meridian:
        engine = SummaryEngine(settings)
        summary = engine.generate_summary(transcript)
        print(f"Generated summary: {summary.title}")

        # 4. Distribute
        distributor = OutputDistributor(settings)
        distributor.to_slack(summary)

        # Create date directory and save files
        date_dir = Path(datetime.now().strftime("%Y-%m-%d"))
        date_dir.mkdir(exist_ok=True)

        slug = slugify(summary.title)
        summary_file = date_dir / f"{slug}.json"
        transcript_file = date_dir / f"transcript_{slug}.txt"

        distributor.to_json(summary, str(summary_file))
        transcript_file.write_text(summary.raw_transcript, encoding="utf-8")
        print(f"Saved: {transcript_file}")

    # 5. Print to console
    _print_summary(summary, summary_file, transcript_file)

    return summary


def _print_summary(summary: MeetingSummary, summary_file: Path, transcript_file: Path) -> None:
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
            print(
                f"  [{a.get('priority', '?').upper()}] {a['task']}"
                f" → {a['owner']} (due: {a.get('deadline', 'TBD')})"
            )

    if summary.follow_ups:
        print("\nFollow-ups:")
        for fu in summary.follow_ups:
            print(f"  • {fu['item']} → {fu['owner']} (by {fu.get('due_date', 'TBD')})")

    print(f"\nSummary saved to: {summary_file}")
    print(f"Transcript saved to: {transcript_file}")
