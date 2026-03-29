"""LLM response parsing utilities."""

import json


def extract_text_block(response) -> str:
    """Extract the first text block from an Anthropic Message, skipping ThinkingBlocks."""
    return next(block.text for block in response.content if block.type == "text")


def parse_llm_json(raw_text: str) -> dict:
    """Extract the first JSON object from an LLM response.

    Handles markdown fences and trailing commentary.
    """
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text[: -len("```")]
    text = text.strip()

    decoder = json.JSONDecoder()
    data, _ = decoder.raw_decode(text)
    return data
