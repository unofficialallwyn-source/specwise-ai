"""Token usage tracking for SpecWise AI graph runs."""

from typing import Any, Dict, List

from src.app_logging import get_logger, log_event

logger = get_logger(__name__)

TOKEN_USAGE_LOG = []


def extract_usage(response: Any) -> Dict[str, int]:
    """
    Extracts token usage from LangChain AIMessage response.
    Handles both usage_metadata and response_metadata formats.
    """

    usage = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "cached_tokens": 0,
    }

    usage_metadata = getattr(response, "usage_metadata", None)

    if usage_metadata:
        usage["input_tokens"] = usage_metadata.get("input_tokens", 0)
        usage["output_tokens"] = usage_metadata.get("output_tokens", 0)
        usage["total_tokens"] = usage_metadata.get("total_tokens", 0)
        return usage

    response_metadata = getattr(response, "response_metadata", {}) or {}
    token_usage = response_metadata.get("token_usage", {}) or {}

    usage["input_tokens"] = token_usage.get("prompt_tokens", 0)
    usage["output_tokens"] = token_usage.get("completion_tokens", 0)
    usage["total_tokens"] = token_usage.get("total_tokens", 0)

    prompt_details = token_usage.get("prompt_tokens_details", {}) or {}
    usage["cached_tokens"] = prompt_details.get("cached_tokens", 0)

    return usage


def log_token_usage(node_name: str, response: Any) -> None:
    """
    Adds token usage for each LLM node call into TOKEN_USAGE_LOG.
    """

    usage = extract_usage(response)

    token_row = {
        "node": node_name,
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "total_tokens": usage["total_tokens"],
        "cached_tokens": usage["cached_tokens"],
    }

    TOKEN_USAGE_LOG.append(token_row)
    log_event(logger, "token_usage_recorded", **token_row)


def print_token_report() -> None:
    """
    Logs token usage summary for the current graph run.
    """

    if not TOKEN_USAGE_LOG:
        log_event(logger, "token_report_empty")
        return

    total_input = sum(row["input_tokens"] for row in TOKEN_USAGE_LOG)
    total_output = sum(row["output_tokens"] for row in TOKEN_USAGE_LOG)
    total_tokens = sum(row["total_tokens"] for row in TOKEN_USAGE_LOG)
    total_cached = sum(row["cached_tokens"] for row in TOKEN_USAGE_LOG)

    log_event(
        logger,
        "token_report_summary",
        total_input_tokens=total_input,
        total_output_tokens=total_output,
        total_tokens=total_tokens,
        total_cached_tokens=total_cached,
        node_count=len(TOKEN_USAGE_LOG),
    )


def clear_token_usage() -> None:
    TOKEN_USAGE_LOG.clear()
    log_event(logger, "token_usage_cleared")


def get_token_report() -> List[Dict[str, int]]:
    return TOKEN_USAGE_LOG.copy()
