"""Custom exceptions for SpecWise AI."""

from typing import Optional


class SpecWiseError(Exception):
    """Base exception with a safe message that can be shown in the UI."""

    def __init__(self, message: str, user_message: Optional[str] = None):
        super().__init__(message)
        self.user_message = user_message or message


class ConfigurationError(SpecWiseError):
    """Raised when required runtime configuration is missing or invalid."""


class LLMInvocationError(SpecWiseError):
    """Raised when the LLM call fails after retries."""


class LLMResponseParseError(SpecWiseError):
    """Raised when the LLM response cannot be parsed as JSON."""
