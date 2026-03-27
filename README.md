# 🎙️ Meeting Summarizer

> Automatically transcribe, diarize, and summarize meetings using **Whisper** (local) + **Claude** (cloud).

Supports **English and Chinese (Mandarin)** conversations out of the box.

---

## Features

- 🔒 **Privacy-first** — audio is transcribed locally via [OpenAI Whisper](https://github.com/openai/whisper); no audio ever leaves your machine
- 👥 **Speaker identification** — powered by [pyannote.audio](https://github.com/pyannote/pyannote-audio)
- 🧠 **Structured summaries** — Claude extracts decisions, action items, follow-ups, and sentiment
- 🌏 **Bilingual** — handles mixed English/Chinese transcripts natively
- 📤 **Flexible output** — JSON export + optional Slack posting

## Pipeline

```
Audio File
  └─▶ Whisper (local transcription)
        └─▶ pyannote (speaker diarization)
              └─▶ Claude (structured summary)
                    ├─▶ JSON file
                    └─▶ Slack (optional)
```

---

## Requirements

- Python ≥ 3.11
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- [HuggingFace account](https://huggingface.co) + token (for speaker diarization)
- [Anthropic API key](https://console.anthropic.com)

---

## Setup

### 1. Install uv (if not already)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and install

```bash
git clone https://github.com/HiIAmTzeKean/meeting-summarizer.git
cd meeting-summarizer
uv sync
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | [Anthropic Console](https://console.anthropic.com) |
| `HF_TOKEN` | ✅ | [HuggingFace token](https://huggingface.co/settings/tokens) — also accept [model terms](https://huggingface.co/pyannote/speaker-diarization-3.1) |
| `WHISPER_MODEL` | ➖ | `tiny` / `base` / `small` / `medium` / `large` (default: `medium`) |
| `MEETING_LANGUAGE` | ➖ | `auto` / `en` / `zh` (default: `auto`) |
| `SLACK_WEBHOOK_URL` | ➖ | Optional Slack webhook for posting summaries |

### 4. Download the Whisper model (one-time)

```bash
uv run download-model
```

The model is saved to `~/.cache/whisper/` and reused offline after this step.

---

## Usage

```bash
uv run meeting-summarizer path/to/meeting.wav
```

Output is printed to the console and saved as `meeting_YYYY-MM-DD.json`.

---

## Project Structure

```
meeting-summarizer/
├── src/
│   └── meeting_summarizer/
│       ├── __init__.py
│       ├── transcriber.py      # Whisper-based local transcription
│       ├── diarizer.py         # Speaker identification (pyannote)
│       ├── summary_engine.py   # Claude-powered structured summary
│       ├── distributor.py      # Output: Slack / JSON
│       ├── main.py             # CLI entry point
│       └── download_model.py   # One-time model download utility
├── tests/
│   └── test_transcriber.py
├── .env.example
├── pyproject.toml              # Project metadata, deps, ruff, pytest config
└── README.md
```

---

## Development

```bash
# Install with dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Lint + format
uv run ruff check src tests
uv run ruff format src tests
```

---

## Tips

- Use `WHISPER_MODEL=medium` for the best speed/accuracy balance on English + Chinese
- For meetings longer than 2 hours, consider splitting audio into 30-minute chunks
- Add a speaker name mapping in `diarizer.py` to replace `SPEAKER_00` labels with real names
- Iterate on the Claude prompt in `summary_engine.py` to match your team's output needs

---

## License

MIT
