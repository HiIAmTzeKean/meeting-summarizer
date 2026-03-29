"""Centralized configuration — load .env once, expose a Settings object."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    # Whisper
    whisper_model: str = os.getenv("WHISPER_MODEL", "medium")
    meeting_language: str = os.getenv("MEETING_LANGUAGE", "auto")

    # Anthropic / Claude
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    anthropic_base_url: str | None = os.getenv("ANTHROPIC_BASE_URL")

    # HuggingFace (pyannote diarization)
    hf_token: str | None = os.getenv("HF_TOKEN")

    # Meridian proxy
    meridian_startup_timeout: int = int(os.getenv("MERIDIAN_STARTUP_TIMEOUT", "10"))

    # Integrations
    slack_webhook_url: str | None = os.getenv("SLACK_WEBHOOK_URL")
    notion_token: str | None = os.getenv("NOTION_TOKEN")
    notion_database_id: str | None = os.getenv("NOTION_DATABASE_ID")
