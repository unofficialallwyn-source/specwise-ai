# This file will contain the code to display the tokens consumed by each node

from typing import Dict, Any, List

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
        "cached_tokens": 0
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

    TOKEN_USAGE_LOG.append({
        "node": node_name,
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "total_tokens": usage["total_tokens"],
        "cached_tokens": usage["cached_tokens"]
    })

def print_token_report() -> None:
    """
    Prints token usage summary for the current graph run.
    """

    if not TOKEN_USAGE_LOG:
        print("No token usage recorded.")
        return

    total_input = sum(row["input_tokens"] for row in TOKEN_USAGE_LOG)
    total_output = sum(row["output_tokens"] for row in TOKEN_USAGE_LOG)
    total_tokens = sum(row["total_tokens"] for row in TOKEN_USAGE_LOG)
    total_cached = sum(row["cached_tokens"] for row in TOKEN_USAGE_LOG)

    print("Token Usage by Node")
    print("-" * 80)

    for row in TOKEN_USAGE_LOG:
        print(
            f"{row['node']}: "
            f"input={row['input_tokens']}, "
            f"output={row['output_tokens']}, "
            f"total={row['total_tokens']}, "
            f"cached={row['cached_tokens']}"
        )

    print("-" * 80)
    print(f"Total input tokens  : {total_input}")
    print(f"Total output tokens : {total_output}")
    print(f"Total tokens        : {total_tokens}")
    print(f"Cached tokens       : {total_cached}")

def clear_token_usage():
    TOKEN_USAGE_LOG.clear()

def get_token_report() -> List[Dict[str, int]]:
    return TOKEN_USAGE_LOG.copy()
