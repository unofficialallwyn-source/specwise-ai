"""Tests for LLM runtime configuration validation."""

import pytest

from src import config as config_module
from src.exceptions import ConfigurationError
from src.llm_config import validate_runtime_config


def clear_config_cache() -> None:
    config_module.get_properties.cache_clear()
    config_module.get_config.cache_clear()


def write_properties(tmp_path, content: str):
    properties_file = tmp_path / "specwise.properties"
    properties_file.write_text(content, encoding="utf-8")
    return properties_file


def test_validate_runtime_config_accepts_openai_provider(monkeypatch, tmp_path):
    properties_file = write_properties(
        tmp_path,
        "\n".join(
            [
                "SPECWISE_LLM_PROVIDER=openai",
                "SPECWISE_LLM_API_KEY_ENV=OPENAI_API_KEY",
            ]
        ),
    )

    monkeypatch.setenv("SPECWISE_PROPERTIES_PATH", str(properties_file))
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    clear_config_cache()

    validate_runtime_config()


def test_validate_runtime_config_rejects_unsupported_provider(monkeypatch, tmp_path):
    properties_file = write_properties(tmp_path, "SPECWISE_LLM_PROVIDER=unsupported\n")

    monkeypatch.setenv("SPECWISE_PROPERTIES_PATH", str(properties_file))
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    clear_config_cache()

    with pytest.raises(ConfigurationError):
        validate_runtime_config()


def test_validate_runtime_config_requires_configured_key(monkeypatch, tmp_path):
    properties_file = write_properties(
        tmp_path,
        "\n".join(
            [
                "SPECWISE_LLM_PROVIDER=openai",
                "SPECWISE_LLM_API_KEY_ENV=MISSING_LLM_KEY",
            ]
        ),
    )

    monkeypatch.setenv("SPECWISE_PROPERTIES_PATH", str(properties_file))
    monkeypatch.delenv("MISSING_LLM_KEY", raising=False)
    clear_config_cache()

    with pytest.raises(ConfigurationError):
        validate_runtime_config()


def test_validate_runtime_config_requires_base_url_for_openai_compatible(monkeypatch, tmp_path):
    properties_file = write_properties(
        tmp_path,
        "\n".join(
            [
                "SPECWISE_LLM_PROVIDER=openai_compatible",
                "SPECWISE_LLM_API_KEY_ENV=CUSTOM_LLM_KEY",
                "SPECWISE_LLM_BASE_URL=",
            ]
        ),
    )

    monkeypatch.setenv("SPECWISE_PROPERTIES_PATH", str(properties_file))
    monkeypatch.setenv("CUSTOM_LLM_KEY", "test-key")
    clear_config_cache()

    with pytest.raises(ConfigurationError):
        validate_runtime_config()
