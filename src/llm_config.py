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


def validate_runtime_config() -> None:
    """Validate required runtime configuration before graph execution."""
    config = get_config()

    if not config.openai_api_key:
        raise ConfigurationError(
            "OPENAI_API_KEY is not configured.",
            user_message=(
                "OPENAI_API_KEY is missing. Add it to your .env file or Codespaces secrets "
                "before generating a SpecWise AI document."
            ),
        )


def get_llm() -> ChatOpenAI:
    """Create a configured ChatOpenAI client."""
    validate_runtime_config()
    config = get_config()

    return ChatOpenAI(
        model=config.model_name,
        temperature=config.temperature,
        timeout=config.llm_timeout_seconds,
        max_retries=config.llm_max_retries,
    )
