"""Anthropic API client wrapper."""

import anthropic

from meeting_summarizer.config import Settings


class AnthropicClient:
    """Thin wrapper around the Anthropic SDK.

    Handles API key resolution and proxy (meridian) configuration.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or Settings()
        api_key = settings.anthropic_api_key
        base_url = settings.anthropic_base_url

        if not api_key:
            if base_url:
                api_key = "dummy"  # proxy ignores the key; SDK requires a non-empty value
            else:
                raise ValueError(
                    "ANTHROPIC_API_KEY is required when not using a proxy. "
                    "Set it in .env, or set ANTHROPIC_BASE_URL to use the Claude Max proxy."
                )

        kwargs: dict = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = anthropic.Anthropic(**kwargs)

    def stream_message(
        self,
        *,
        model: str,
        max_tokens: int,
        system: str,
        messages: list[dict],
    ) -> anthropic.types.Message:
        """Send a streaming request and return the final assembled Message."""
        with self._client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        ) as stream:
            return stream.get_final_message()
