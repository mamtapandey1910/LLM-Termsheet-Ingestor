"""Custom exception classes for LLM extractor.

Keep exception classes in a separate module so callers can import
and handle specific failure modes cleanly.
"""


class MissingAPIKeyError(RuntimeError):
    """Raised when the OPENAI_API_KEY environment variable is missing."""
    pass


class OpenAIInitializationError(RuntimeError):
    """Raised when the OpenAI client could not be initialized."""
    pass


class OpenAICallError(RuntimeError):
    """Raised when the OpenAI API call repeatedly fails."""
    pass


class LLMParseError(RuntimeError):
    """Raised when the LLM response cannot be parsed."""
    pass


class SchemaValidationError(ValueError):
    """Raised when the parsed result doesn't match the expected schema."""
    pass


def call_with_backoff(
    func,
    *args,
    max_retries: int = 5,
    base_delay: float = 1,
    max_delay: float = 30,
    retry_on: tuple = (Exception,),
    jitter_frac: float = 0.1,
    **kwargs,
):
    """Call `func(*args, **kwargs)` with exponential backoff and jitter.

    Raises OpenAICallError if the call fails after `max_retries` attempts.
    """
    import time
    import random

    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except retry_on as e:
            last_exc = e
            if attempt == max_retries:
                raise OpenAICallError(f"Call failed after {attempt} attempts: {e}")
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            jitter = random.uniform(0, delay * jitter_frac)
            time.sleep(delay + jitter)
    # Should not reach here, but raise if it does
    raise OpenAICallError(f"Call failed: {last_exc}")
