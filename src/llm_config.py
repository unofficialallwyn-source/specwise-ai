"""LLM configuration and shared system instruction for SpecWise AI."""

from langchain_openai import ChatOpenAI

from src.config import get_config
from src.exceptions import ConfigurationError

COMMON_SYSTEM_INSTRUCTION = """
You are SpecWise AI, a Product Owner assistant.

Rules:
- Use only the provided input.
- Do not invent unrelated features.
- Return valid JSON only.
- Do not include markdown.
- Do not include explanations outside JSON.
- Keep output concise and business-readable.
"""

SUPPORTED_LLM_PROVIDERS = {"openai", "openai_compatible"}


def validate_runtime_config() -> None:
    """Validate required runtime configuration before graph execution."""
    config = get_config()

    if config.llm_provider not in SUPPORTED_LLM_PROVIDERS:
        raise ConfigurationError(
            f"Unsupported LLM provider configured: {config.llm_provider}.",
            user_message=(
                "The configured LLM provider is not supported. Use 'openai' or "
                "'openai_compatible' in config/specwise.properties."
            ),
        )

    if not config.llm_api_key:
        raise ConfigurationError(
            f"{config.llm_api_key_env} is not configured.",
            user_message=(
                f"{config.llm_api_key_env} is missing. Add it to your .env file, "
                "Codespaces secrets, or deployment secrets before generating a SpecWise AI document."
            ),
        )

    if config.llm_provider == "openai_compatible" and not config.llm_base_url:
        raise ConfigurationError(
            "SPECWISE_LLM_BASE_URL is required for openai_compatible provider.",
            user_message=(
                "SPECWISE_LLM_BASE_URL is missing. Add the OpenAI-compatible provider "
                "base URL to config/specwise.properties or your environment settings."
            ),
        )


def get_llm() -> ChatOpenAI:
    """Create a configured chat model client."""
    validate_runtime_config()
    config = get_config()

    llm_kwargs = {
        "model": config.model_name,
        "temperature": config.temperature,
        "timeout": config.llm_timeout_seconds,
        "max_retries": config.llm_max_retries,
    }

    if config.llm_provider == "openai_compatible":
        llm_kwargs["api_key"] = config.llm_api_key
        llm_kwargs["base_url"] = config.llm_base_url
    elif config.llm_api_key_env != "OPENAI_API_KEY":
        llm_kwargs["api_key"] = config.llm_api_key

    return ChatOpenAI(**llm_kwargs)
