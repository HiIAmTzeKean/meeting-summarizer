"""Prompt assets for the meeting summarizer."""

from meeting_summarizer.prompts.meeting_summary import SYSTEM_PROMPT
from meeting_summarizer.prompts.templates import USER_PROMPT_TEMPLATE, build_summary_prompt

__all__ = ["SYSTEM_PROMPT", "USER_PROMPT_TEMPLATE", "build_summary_prompt"]
