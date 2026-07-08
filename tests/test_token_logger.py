"""Tests for token usage logging."""

from src import token_logger


class UsageMetadataResponse:
    usage_metadata = {
        "input_tokens": 10,
        "output_tokens": 5,
        "total_tokens": 15,
    }


class ResponseMetadataResponse:
    usage_metadata = None
    response_metadata = {
        "token_usage": {
            "prompt_tokens": 20,
            "completion_tokens": 8,
            "total_tokens": 28,
            "prompt_tokens_details": {
                "cached_tokens": 4,
            },
        }
    }


def test_extract_usage_from_usage_metadata():
    usage = token_logger.extract_usage(UsageMetadataResponse())

    assert usage["input_tokens"] == 10
    assert usage["output_tokens"] == 5
    assert usage["total_tokens"] == 15
    assert usage["cached_tokens"] == 0


def test_extract_usage_from_response_metadata():
    usage = token_logger.extract_usage(ResponseMetadataResponse())

    assert usage["input_tokens"] == 20
    assert usage["output_tokens"] == 8
    assert usage["total_tokens"] == 28
    assert usage["cached_tokens"] == 4


def test_log_token_usage_and_clear_token_usage():
    token_logger.clear_token_usage()

    token_logger.log_token_usage("test_node", ResponseMetadataResponse())
    report = token_logger.get_token_report()

    assert len(report) == 1
    assert report[0]["node"] == "test_node"
    assert report[0]["total_tokens"] == 28

    token_logger.clear_token_usage()
    assert token_logger.get_token_report() == []
