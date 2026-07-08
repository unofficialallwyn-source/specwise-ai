"""Tests for utility helpers."""

import pytest

from src.exceptions import LLMResponseParseError
from src.utils import compact_json, get_state_text, normalize_list, safe_json_parse


class DummyMessage:
    def __init__(self, content):
        self.content = content


def test_get_state_text_handles_string_message_and_list():
    assert get_state_text("hello") == "hello"
    assert get_state_text(DummyMessage("message content")) == "message content"
    assert get_state_text(["one", DummyMessage("two")]) == "one\ntwo"
    assert get_state_text(None) == ""


def test_compact_json_removes_unnecessary_spacing():
    assert compact_json({"a": 1, "b": [2, 3]}) == '{"a":1,"b":[2,3]}'


def test_safe_json_parse_handles_valid_json():
    assert safe_json_parse('{"name":"SpecWise"}') == {"name": "SpecWise"}


def test_safe_json_parse_handles_markdown_code_fence():
    raw_response = "```json\n{\"status\": \"ok\"}\n```"
    assert safe_json_parse(raw_response) == {"status": "ok"}


def test_safe_json_parse_extracts_json_object_from_extra_text():
    raw_response = "Here is the result: {\"count\": 3}"
    assert safe_json_parse(raw_response) == {"count": 3}


def test_safe_json_parse_raises_for_invalid_json():
    with pytest.raises(LLMResponseParseError):
        safe_json_parse("this is not json")


def test_normalize_list_returns_list_of_strings():
    assert normalize_list(None) == []
    assert normalize_list("single") == ["single"]
    assert normalize_list(123) == ["123"]
    assert normalize_list(["a", 2]) == ["a", "2"]
