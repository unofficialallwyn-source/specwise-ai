"""LangGraph node definitions for SpecWise AI."""

import logging
from time import perf_counter
from typing import Any, Dict

from src.app_logging import get_logger, log_event
from src.config import get_config
from src.exceptions import ConfigurationError, LLMInvocationError, LLMResponseParseError
from src.llm_config import COMMON_SYSTEM_INSTRUCTION, get_llm
from src.state import AgentState
from src.token_logger import log_token_usage
from src.utils import compact_json, get_state_text, normalize_list, safe_json_parse

logger = get_logger(__name__)
_llm = None


def get_llm_client():
    """Create the LLM client lazily so app import does not fail without configuration."""
    global _llm

    if _llm is None:
        _llm = get_llm()

    return _llm


def invoke_llm_json(node_name: str, task_instruction: str, input_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke the LLM, log execution details, retry transient failures, and parse JSON."""
    config = get_config()
    max_attempts = max(1, config.llm_max_retries + 1)

    prompt = f"""
{COMMON_SYSTEM_INSTRUCTION}

Task:
{task_instruction}

Input:
{compact_json(input_payload)}
"""

    last_error = None

    for attempt in range(1, max_attempts + 1):
        start_time = perf_counter()
        log_event(logger, "node_execution_started", node=node_name, attempt=attempt, max_attempts=max_attempts)

        try:
            response = get_llm_client().invoke(prompt)
            log_token_usage(node_name, response)
            result = safe_json_parse(response.content)

            duration_ms = round((perf_counter() - start_time) * 1000, 2)
            log_event(logger, "node_execution_completed", node=node_name, attempt=attempt, duration_ms=duration_ms)

            return result
        except ConfigurationError:
            raise
        except LLMResponseParseError as error:
            last_error = error
            duration_ms = round((perf_counter() - start_time) * 1000, 2)
            log_event(
                logger,
                "node_json_parse_failed",
                level=logging.WARNING,
                node=node_name,
                attempt=attempt,
                duration_ms=duration_ms,
                error_message=str(error),
            )

            if attempt == max_attempts:
                raise error
        except Exception as error:
            last_error = error
            duration_ms = round((perf_counter() - start_time) * 1000, 2)
            log_event(
                logger,
                "node_execution_failed",
                level=logging.ERROR,
                node=node_name,
                attempt=attempt,
                duration_ms=duration_ms,
                error_type=type(error).__name__,
                error_message=str(error),
            )

            if attempt == max_attempts:
                raise LLMInvocationError(
                    f"LLM node '{node_name}' failed after {max_attempts} attempts: {error}",
                    user_message=(
                        "SpecWise AI could not complete the AI generation step. "
                        "Please try again in a moment."
                    ),
                ) from error

    raise LLMInvocationError(
        f"LLM node '{node_name}' failed: {last_error}",
        user_message="SpecWise AI could not complete the AI generation step. Please try again.",
    )


def requirement_intake(spec_state: AgentState) -> dict:
    """Non-LLM node that keeps the user-provided requirement as raw_requirement."""
    raw_requirement = get_state_text(spec_state.get("raw_requirement", ""))
    log_event(logger, "requirement_received", character_count=len(raw_requirement))

    return {
        "raw_requirement": raw_requirement,
    }


def requirement_extractor(spec_state: AgentState) -> dict:
    """Extract feature summary, functional requirements, and non-functional requirements."""
    config = get_config()

    task_instruction = f"""
Extract requirement details.

Return this JSON object:
{{
  "feature_summary": "one concise paragraph",
  "functional_requirements": ["max {config.max_functional_requirements} specific functional requirements"],
  "non_functional_requirements": ["max {config.max_non_functional_requirements} relevant non-functional requirements"]
}}

Limits:
- functional_requirements: maximum {config.max_functional_requirements}
- non_functional_requirements: maximum {config.max_non_functional_requirements}
"""

    input_payload = {
        "raw_requirement": get_state_text(spec_state.get("raw_requirement", "")),
    }

    result = invoke_llm_json(
        node_name="requirement_extractor",
        task_instruction=task_instruction,
        input_payload=input_payload,
    )

    return {
        "feature_summary": result.get("feature_summary", ""),
        "functional_requirements": normalize_list(result.get("functional_requirements", [])),
        "non_functional_requirements": normalize_list(result.get("non_functional_requirements", [])),
    }


def role_identifier(spec_state: AgentState) -> dict:
    """Identify user roles from extracted requirements."""
    config = get_config()

    task_instruction = f"""
Identify user roles from the requirement.

Return this JSON object:
{{
  "identified_roles": ["max {config.max_roles} roles"]
}}

Rules:
- Use simple role names such as user, admin, customer, support agent.
- Do not invent unnecessary roles.

Limits:
- identified_roles: maximum {config.max_roles}
"""

    input_payload = {
        "feature_summary": spec_state.get("feature_summary", ""),
        "functional_requirements": spec_state.get("functional_requirements", []),
    }

    result = invoke_llm_json(
        node_name="role_identifier",
        task_instruction=task_instruction,
        input_payload=input_payload,
    )

    return {
        "identified_roles": normalize_list(result.get("identified_roles", [])),
    }


def epic_generator(spec_state: AgentState) -> dict:
    """Generate epics from functional requirements and roles."""
    config = get_config()

    task_instruction = f"""
Generate high-level product epics.

Return this JSON object:
{{
  "epics": ["max {config.max_epics} epics"]
}}

Rules:
- Group related requirements together.
- Keep each epic short and clear.
- Do not add features not present in the input.

Limits:
- epics: maximum {config.max_epics}
"""

    input_payload = {
        "functional_requirements": spec_state.get("functional_requirements", []),
        "identified_roles": spec_state.get("identified_roles", []),
    }

    result = invoke_llm_json(
        node_name="epic_generator",
        task_instruction=task_instruction,
        input_payload=input_payload,
    )

    return {
        "epics": normalize_list(result.get("epics", [])),
    }


def user_story_generator(spec_state: AgentState) -> dict:
    """Generate user stories from epics, roles, and functional requirements."""
    config = get_config()

    task_instruction = f"""
Generate user stories.

Return this JSON object:
{{
  "user_stories": ["max {config.max_user_stories} user stories"]
}}

Rules:
- Use this format: As a <role>, I want <capability> so that <benefit>.
- Use only the provided epics, roles, and requirements.
- Do not create unrelated user stories.

Limits:
- user_stories: maximum {config.max_user_stories}
"""

    input_payload = {
        "epics": spec_state.get("epics", []),
        "identified_roles": spec_state.get("identified_roles", []),
        "functional_requirements": spec_state.get("functional_requirements", []),
    }

    result = invoke_llm_json(
        node_name="user_story_generator",
        task_instruction=task_instruction,
        input_payload=input_payload,
    )

    return {
        "user_stories": normalize_list(result.get("user_stories", [])),
    }


def acceptance_criteria_generator(spec_state: AgentState) -> dict:
    """Generate acceptance criteria from user stories."""
    config = get_config()

    task_instruction = f"""
Generate acceptance criteria.

Return this JSON object:
{{
  "acceptance_criteria": ["max {config.max_acceptance_criteria} acceptance criteria"]
}}

Rules:
- Prefer Given/When/Then style.
- Keep each criterion testable.
- Use only the provided user stories.

Limits:
- acceptance_criteria: maximum {config.max_acceptance_criteria}
"""

    input_payload = {
        "user_stories": spec_state.get("user_stories", []),
    }

    result = invoke_llm_json(
        node_name="acceptance_criteria_generator",
        task_instruction=task_instruction,
        input_payload=input_payload,
    )

    return {
        "acceptance_criteria": normalize_list(result.get("acceptance_criteria", [])),
    }


def gap_detector(spec_state: AgentState) -> dict:
    """Identify open questions and missing requirement details."""
    config = get_config()

    task_instruction = f"""
Identify open questions for the Product Owner or client.

Return this JSON object:
{{
  "open_questions": ["max {config.max_open_questions} open questions"]
}}

Rules:
- Questions should be practical and useful for requirement clarification.
- Do not ask questions already answered by the input.

Limits:
- open_questions: maximum {config.max_open_questions}
"""

    input_payload = {
        "raw_requirement": get_state_text(spec_state.get("raw_requirement", "")),
        "functional_requirements": spec_state.get("functional_requirements", []),
    }

    result = invoke_llm_json(
        node_name="gap_detector",
        task_instruction=task_instruction,
        input_payload=input_payload,
    )

    return {
        "open_questions": normalize_list(result.get("open_questions", [])),
    }


def risk_assumption_analyzer(spec_state: AgentState) -> dict:
    """Identify assumptions, risks, and dependencies."""
    config = get_config()

    task_instruction = f"""
Identify assumptions, risks, and dependencies.

Return this JSON object:
{{
  "assumptions": ["max {config.max_assumptions} assumptions"],
  "risks": ["max {config.max_risks} risks"],
  "dependencies": ["max {config.max_dependencies} dependencies"]
}}

Rules:
- Keep items specific to the provided requirements.
- Do not include unrelated business or technical items.

Limits:
- assumptions: maximum {config.max_assumptions}
- risks: maximum {config.max_risks}
- dependencies: maximum {config.max_dependencies}
"""

    input_payload = {
        "functional_requirements": spec_state.get("functional_requirements", []),
        "non_functional_requirements": spec_state.get("non_functional_requirements", []),
    }

    result = invoke_llm_json(
        node_name="risk_assumption_analyzer",
        task_instruction=task_instruction,
        input_payload=input_payload,
    )

    return {
        "assumptions": normalize_list(result.get("assumptions", [])),
        "risks": normalize_list(result.get("risks", [])),
        "dependencies": normalize_list(result.get("dependencies", [])),
    }


def test_scenario_generator(spec_state: AgentState) -> dict:
    """Generate test scenarios from user stories and acceptance criteria."""
    config = get_config()

    task_instruction = f"""
Generate high-level test scenarios.

Return this JSON object:
{{
  "test_scenarios": ["max {config.max_test_scenarios} test scenarios"]
}}

Rules:
- Each scenario should be clear and testable.
- Use only the provided user stories and acceptance criteria.

Limits:
- test_scenarios: maximum {config.max_test_scenarios}
"""

    input_payload = {
        "user_stories": spec_state.get("user_stories", []),
        "acceptance_criteria": spec_state.get("acceptance_criteria", []),
    }

    result = invoke_llm_json(
        node_name="test_scenario_generator",
        task_instruction=task_instruction,
        input_payload=input_payload,
    )

    return {
        "test_scenarios": normalize_list(result.get("test_scenarios", [])),
    }
