# src/utils/rate_limit.py
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from groq import RateLimitError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Decorator to wrap any LLM call
def groq_retry_decorator(func):
    return retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type(RateLimitError),
        before_sleep=lambda retry_state: logger.warning(
            f"⚠️ Rate limit hit. Retrying in {retry_state.next_action.sleep} seconds..."
        )
    )(func)
