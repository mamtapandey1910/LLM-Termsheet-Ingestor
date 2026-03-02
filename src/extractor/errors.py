"""Custom exception classes and helpers for the LLM extractor.

This module exposes a single base exception `ExtractorError` which all
extractor-specific errors subclass. It also includes a reusable
`call_with_backoff` helper that callers may use to perform retries with
exponential backoff and jitter.
"""

from __future__ import annotations

from typing import Any, Callable


class ExtractorError(Exception):
    """Base class for extractor-related errors."""
    pass


class MissingAPIKeyError(ExtractorError, RuntimeError):
    """Raised when the OPENAI_API_KEY environment variable is missing."""
    pass


class OpenAIInitializationError(ExtractorError, RuntimeError):
    """Raised when the OpenAI client could not be initialized."""
    pass


class OpenAICallError(ExtractorError, RuntimeError):
    """Raised when the OpenAI API call repeatedly fails."""
    pass


class LLMParseError(ExtractorError, RuntimeError):
    """Raised when the LLM response cannot be parsed."""
    pass


class SchemaValidationError(ExtractorError, ValueError):
    """Raised when the parsed result doesn't match the expected schema."""
    pass


def call_with_backoff(
    func: Callable[..., Any],
    *args: Any,
    max_retries: int = 5,
    base_delay: float = 1,
    max_delay: float = 30,
    retry_on: tuple = (Exception,),
    jitter_frac: float = 0,
    **kwargs: Any,
) -> Any:
    """Call `func(*args, **kwargs)` with exponential backoff and jitter.

    On repeated failures this raises :class:`OpenAICallError` with the
    last caught exception message.
    """
    import time
    import random

    last_exc: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except retry_on as e:  # type: ignore[exc]
            last_exc = e
            if attempt == max_retries:
                raise OpenAICallError(f"Call failed after {attempt} attempts: {e}")
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            jitter = random.uniform(0, delay * jitter_frac)
            time.sleep(delay + jitter)

    # Fallback if loop exits unexpectedly
    raise OpenAICallError(f"Call failed: {last_exc}")
