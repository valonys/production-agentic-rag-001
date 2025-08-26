import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger()

def retry_with_backoff(retries=3, backoff_in_seconds=1):
    return retry(
        stop=stop_after_attempt(retries),
        wait=wait_exponential(multiplier=backoff_in_seconds, min=1, max=10),
    )
