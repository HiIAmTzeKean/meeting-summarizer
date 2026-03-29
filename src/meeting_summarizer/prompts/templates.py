"""User prompt templates."""

import textwrap


USER_PROMPT_TEMPLATE = textwrap.dedent("""\
    Transcript:
    {transcript}""")


def build_summary_prompt(transcript: str) -> str:
    """Format the user prompt with the given transcript text."""
    return USER_PROMPT_TEMPLATE.format(transcript=transcript)
