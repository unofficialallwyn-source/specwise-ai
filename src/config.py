"""Application configuration for SpecWise AI."""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROPERTIES_PATH = PROJECT_ROOT / "config" / "specwise.properties"


def _load_properties_file() -> Dict[str, str]:
    """Load non-secret application properties from config/specwise.properties."""
    properties_path = Path(os.getenv("SPECWISE_PROPERTIES_PATH", DEFAULT_PROPERTIES_PATH))

    if not properties_path.exists():
        return {}

    properties: Dict[str, str] = {}

    with properties_path.open("r", encoding="utf-8") as properties_file:
        for line in properties_file:
            stripped_line = line.strip()

            if not stripped_line or stripped_line.startswith("#"):
                continue

            if "=" not in stripped_line:
                continue

            key, value = stripped_line.split("=", 1)
            properties[key.strip()] = value.strip()

    return properties


@lru_cache(maxsize=1)
def get_properties() -> Dict[str, str]:
    """Return cached non-secret application properties."""
    return _load_properties_file()


def _get_value(name: str, default: str) -> str:
    """
    Resolve a config value using this priority:
    1. Environment variable or .env
    2. config/specwise.properties
    3. Safe default from code
    """
    env_value = os.getenv(name)

    if env_value is not None and env_value.strip() != "":
        return env_value.strip()

    property_value = get_properties().get(name)

    if property_value is not None and property_value.strip() != "":
        return property_value.strip()

    return default


def _get_optional_value(name: str, default: str = "") -> Optional[str]:
    value = _get_value(name, default).strip()
    return value or None


def _get_int(name: str, default: int) -> int:
    value = _get_value(name, str(default))

    try:
        return int(value)
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    value = _get_value(name, str(default))

    try:
        return float(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class AppConfig:
    """Runtime configuration loaded from environment variables and properties file."""

    openai_api_key: Optional[str]
    llm_provider: str
    llm_api_key_env: str
    llm_base_url: Optional[str]
    model_name: str
    temperature: float
    llm_max_retries: int
    llm_timeout_seconds: int
    max_functional_requirements: int
    max_non_functional_requirements: int
    max_roles: int
    max_epics: int
    max_user_stories: int
    max_acceptance_criteria: int
    max_open_questions: int
    max_assumptions: int
    max_risks: int
    max_dependencies: int
    max_test_scenarios: int

    @property
    def llm_api_key(self) -> Optional[str]:
        """Read the configured provider API key from the configured environment variable."""
        return os.getenv(self.llm_api_key_env)

    @property
    def output_limits(self) -> Dict[str, int]:
        """Expose output limits in a single dictionary for prompts and UI."""
        return {
            "functional_requirements": self.max_functional_requirements,
            "non_functional_requirements": self.max_non_functional_requirements,
            "identified_roles": self.max_roles,
            "epics": self.max_epics,
            "user_stories": self.max_user_stories,
            "acceptance_criteria": self.max_acceptance_criteria,
            "open_questions": self.max_open_questions,
            "assumptions": self.max_assumptions,
            "risks": self.max_risks,
            "dependencies": self.max_dependencies,
            "test_scenarios": self.max_test_scenarios,
        }


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Load configuration once per application process."""
    llm_api_key_env = _get_value("SPECWISE_LLM_API_KEY_ENV", "OPENAI_API_KEY")

    return AppConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        llm_provider=_get_value("SPECWISE_LLM_PROVIDER", "openai").lower(),
        llm_api_key_env=llm_api_key_env,
        llm_base_url=_get_optional_value("SPECWISE_LLM_BASE_URL"),
        model_name=_get_value("SPECWISE_MODEL", "gpt-4o"),
        temperature=_get_float("SPECWISE_TEMPERATURE", 0.0),
        llm_max_retries=_get_int("SPECWISE_LLM_MAX_RETRIES", 2),
        llm_timeout_seconds=_get_int("SPECWISE_LLM_TIMEOUT_SECONDS", 60),
        max_functional_requirements=_get_int("SPECWISE_MAX_FUNCTIONAL_REQUIREMENTS", 5),
        max_non_functional_requirements=_get_int("SPECWISE_MAX_NON_FUNCTIONAL_REQUIREMENTS", 5),
        max_roles=_get_int("SPECWISE_MAX_ROLES", 4),
        max_epics=_get_int("SPECWISE_MAX_EPICS", 3),
        max_user_stories=_get_int("SPECWISE_MAX_USER_STORIES", 5),
        max_acceptance_criteria=_get_int("SPECWISE_MAX_ACCEPTANCE_CRITERIA", 5),
        max_open_questions=_get_int("SPECWISE_MAX_OPEN_QUESTIONS", 5),
        max_assumptions=_get_int("SPECWISE_MAX_ASSUMPTIONS", 5),
        max_risks=_get_int("SPECWISE_MAX_RISKS", 5),
        max_dependencies=_get_int("SPECWISE_MAX_DEPENDENCIES", 5),
        max_test_scenarios=_get_int("SPECWISE_MAX_TEST_SCENARIOS", 6),
    )
