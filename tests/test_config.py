"""Tests for SpecWise AI configuration loading."""

from src import config as config_module


def clear_config_cache() -> None:
    config_module.get_properties.cache_clear()
    config_module.get_config.cache_clear()


def test_properties_file_values_are_loaded(monkeypatch, tmp_path):
    properties_file = tmp_path / "specwise.properties"
    properties_file.write_text(
        "\n".join(
            [
                "SPECWISE_LLM_PROVIDER=openai_compatible",
                "SPECWISE_LLM_API_KEY_ENV=CUSTOM_LLM_KEY",
                "SPECWISE_LLM_BASE_URL=https://example.com/v1",
                "SPECWISE_MODEL=gpt-test-model",
                "SPECWISE_TEMPERATURE=0.2",
                "SPECWISE_LLM_MAX_RETRIES=4",
                "SPECWISE_MAX_EPICS=7",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("SPECWISE_PROPERTIES_PATH", str(properties_file))
    monkeypatch.setenv("CUSTOM_LLM_KEY", "test-key")
    monkeypatch.delenv("SPECWISE_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("SPECWISE_LLM_API_KEY_ENV", raising=False)
    monkeypatch.delenv("SPECWISE_LLM_BASE_URL", raising=False)
    monkeypatch.delenv("SPECWISE_MODEL", raising=False)
    monkeypatch.delenv("SPECWISE_TEMPERATURE", raising=False)
    monkeypatch.delenv("SPECWISE_LLM_MAX_RETRIES", raising=False)
    monkeypatch.delenv("SPECWISE_MAX_EPICS", raising=False)
    clear_config_cache()

    app_config = config_module.get_config()

    assert app_config.llm_provider == "openai_compatible"
    assert app_config.llm_api_key_env == "CUSTOM_LLM_KEY"
    assert app_config.llm_api_key == "test-key"
    assert app_config.llm_base_url == "https://example.com/v1"
    assert app_config.model_name == "gpt-test-model"
    assert app_config.temperature == 0.2
    assert app_config.llm_max_retries == 4
    assert app_config.max_epics == 7


def test_environment_variable_overrides_properties_file(monkeypatch, tmp_path):
    properties_file = tmp_path / "specwise.properties"
    properties_file.write_text("SPECWISE_MAX_USER_STORIES=3\n", encoding="utf-8")

    monkeypatch.setenv("SPECWISE_PROPERTIES_PATH", str(properties_file))
    monkeypatch.setenv("SPECWISE_MAX_USER_STORIES", "9")
    clear_config_cache()

    app_config = config_module.get_config()

    assert app_config.max_user_stories == 9


def test_safe_defaults_are_used_when_properties_are_missing(monkeypatch, tmp_path):
    missing_properties_file = tmp_path / "missing.properties"

    monkeypatch.setenv("SPECWISE_PROPERTIES_PATH", str(missing_properties_file))
    monkeypatch.delenv("SPECWISE_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("SPECWISE_LLM_API_KEY_ENV", raising=False)
    monkeypatch.delenv("SPECWISE_LLM_BASE_URL", raising=False)
    monkeypatch.delenv("SPECWISE_MODEL", raising=False)
    monkeypatch.delenv("SPECWISE_MAX_TEST_SCENARIOS", raising=False)
    clear_config_cache()

    app_config = config_module.get_config()

    assert app_config.llm_provider == "openai"
    assert app_config.llm_api_key_env == "OPENAI_API_KEY"
    assert app_config.llm_base_url is None
    assert app_config.model_name == "gpt-4o"
    assert app_config.max_test_scenarios == 6
