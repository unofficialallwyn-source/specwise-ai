# This file will contain the definition for various nodes in the LangGraph

from src.llm_config import get_llm, COMMON_SYSTEM_INSTRUCTION
from src.token_logger import log_token_usage
from src.utils import get_state_text, normalize_list, compact_json, safe_json_parse

llm = get_llm()

def invoke_llm_json(node_name, task_instruction, input_payload):
    prompt = f"""
{COMMON_SYSTEM_INSTRUCTION}

Task:
{task_instruction}

Input:
{compact_json(input_payload)}
"""

    response = llm.invoke(prompt)
    log_token_usage(node_name, response)
    return safe_json_parse(response.content)

def requirement_intake(spec_state: AgentState-> dict:
    """
    Non-LLM node.
    Keeps the user-provided requirement as raw_requirement.
    """

    raw_requirement = get_state_text(spec_state.get("raw_requirement", ""))

    return {
        "raw_requirement": raw_requirement
    }


def requirement_extractor(spec_state: AgentState-> dict:
    """
    LLM node.
    Extracts feature summary, functional requirements, and non-functional requirements.
    """

    task_instruction = """
Extract requirement details.

Return this JSON object:
{
  "feature_summary": "one concise paragraph",
  "functional_requirements": ["max 5 specific functional requirements"],
  "non_functional_requirements": ["max 5 relevant non-functional requirements"]
}

Limits:
- functional_requirements: maximum 5
- non_functional_requirements: maximum 5
"""

    input_payload = {
        "raw_requirement": get_state_text(spec_state.get("raw_requirement", ""))
    }

    result = invoke_llm_json(
        node_name="requirement_extractor",
        task_instruction=task_instruction,
        input_payload=input_payload
    )

    return {
        "feature_summary": result.get("feature_summary", ""),
        "functional_requirements": normalize_list(result.get("functional_requirements", [])),
        "non_functional_requirements": normalize_list(result.get("non_functional_requirements", []))
    }


def role_identifier(spec_state: AgentState-> dict:
    """
    LLM node.
    Identifies user roles from extracted requirements.
    """

    task_instruction = """
Identify user roles from the requirement.

Return this JSON object:
{
  "identified_roles": ["max 4 roles"]
}

Rules:
- Use simple role names such as user, admin, customer, support agent.
- Do not invent unnecessary roles.

Limits:
- identified_roles: maximum 4
"""

    input_payload = {
        "feature_summary": spec_state.get("feature_summary", ""),
        "functional_requirements": spec_state.get("functional_requirements", [])
    }

    result = invoke_llm_json(
        node_name="role_identifier",
        task_instruction=task_instruction,
        input_payload=input_payload
    )

    return {
        "identified_roles": normalize_list(result.get("identified_roles", []))
    }


def epic_generator(spec_state: AgentState-> dict:
    """
    LLM node.
    Generates epics from functional requirements and roles.
    """

    task_instruction = """
Generate high-level product epics.

Return this JSON object:
{
  "epics": ["max 3 epics"]
}

Rules:
- Group related requirements together.
- Keep each epic short and clear.
- Do not add features not present in the input.

Limits:
- epics: maximum 3
"""

    input_payload = {
        "functional_requirements": spec_state.get("functional_requirements", []),
        "identified_roles": spec_state.get("identified_roles", [])
    }

    result = invoke_llm_json(
        node_name="epic_generator",
        task_instruction=task_instruction,
        input_payload=input_payload
    )

    return {
        "epics": normalize_list(result.get("epics", []))
    }


def user_story_generator(spec_state: AgentState-> dict:
    """
    LLM node.
    Generates user stories from epics, roles, and functional requirements.
    """

    task_instruction = """
Generate user stories.

Return this JSON object:
{
  "user_stories": ["max 5 user stories"]
}

Rules:
- Use this format: As a <role>, I want <capability> so that <benefit>.
- Use only the provided epics, roles, and requirements.
- Do not create unrelated user stories.

Limits:
- user_stories: maximum 5
"""

    input_payload = {
        "epics": spec_state.get("epics", []),
        "identified_roles": spec_state.get("identified_roles", []),
        "functional_requirements": spec_state.get("functional_requirements", [])
    }

    result = invoke_llm_json(
        node_name="user_story_generator",
        task_instruction=task_instruction,
        input_payload=input_payload
    )

    return {
        "user_stories": normalize_list(result.get("user_stories", []))
    }


def acceptance_criteria_generator(spec_state: AgentState-> dict:
    """
    LLM node.
    Generates acceptance criteria from user stories.
    """

    task_instruction = """
Generate acceptance criteria.

Return this JSON object:
{
  "acceptance_criteria": ["max 5 acceptance criteria"]
}

Rules:
- Prefer Given/When/Then style.
- Keep each criterion testable.
- Use only the provided user stories.

Limits:
- acceptance_criteria: maximum 5
"""

    input_payload = {
        "user_stories": spec_state.get("user_stories", [])
    }

    result = invoke_llm_json(
        node_name="acceptance_criteria_generator",
        task_instruction=task_instruction,
        input_payload=input_payload
    )

    return {
        "acceptance_criteria": normalize_list(result.get("acceptance_criteria", []))
    }


def gap_detector(spec_state: AgentState-> dict:
    """
    LLM node.
    Identifies open questions and missing requirement details.
    """

    task_instruction = """
Identify open questions for the Product Owner or client.

Return this JSON object:
{
  "open_questions": ["max 5 open questions"]
}

Rules:
- Questions should be practical and useful for requirement clarification.
- Do not ask questions already answered by the input.

Limits:
- open_questions: maximum 5
"""

    input_payload = {
        "raw_requirement": get_state_text(spec_state.get("raw_requirement", "")),
        "functional_requirements": spec_state.get("functional_requirements", [])
    }

    result = invoke_llm_json(
        node_name="gap_detector",
        task_instruction=task_instruction,
        input_payload=input_payload
    )

    return {
        "open_questions": normalize_list(result.get("open_questions", []))
    }


def risk_assumption_analyzer(spec_state: AgentState-> dict:
    """
    LLM node.
    Identifies assumptions, risks, and dependencies.
    """

    task_instruction = """
Identify assumptions, risks, and dependencies.

Return this JSON object:
{
  "assumptions": ["max 5 assumptions"],
  "risks": ["max 5 risks"],
  "dependencies": ["max 5 dependencies"]
}

Rules:
- Keep items specific to the provided requirements.
- Do not include unrelated business or technical items.

Limits:
- assumptions: maximum 5
- risks: maximum 5
- dependencies: maximum 5
"""

    input_payload = {
        "functional_requirements": spec_state.get("functional_requirements", []),
        "non_functional_requirements": spec_state.get("non_functional_requirements", [])
    }

    result = invoke_llm_json(
        node_name="risk_assumption_analyzer",
        task_instruction=task_instruction,
        input_payload=input_payload
    )

    return {
        "assumptions": normalize_list(result.get("assumptions", [])),
        "risks": normalize_list(result.get("risks", [])),
        "dependencies": normalize_list(result.get("dependencies", []))
    }


def test_scenario_generator(spec_state: AgentState-> dict:
    """
    LLM node.
    Generates test scenarios from user stories and acceptance criteria.
    """

    task_instruction = """
Generate high-level test scenarios.

Return this JSON object:
{
  "test_scenarios": ["max 6 test scenarios"]
}

Rules:
- Each scenario should be clear and testable.
- Use only the provided user stories and acceptance criteria.

Limits:
- test_scenarios: maximum 6
"""

    input_payload = {
        "user_stories": spec_state.get("user_stories", []),
        "acceptance_criteria": spec_state.get("acceptance_criteria", [])
    }

    result = invoke_llm_json(
        node_name="test_scenario_generator",
        task_instruction=task_instruction,
        input_payload=input_payload
    )

    return {
        "test_scenarios": normalize_list(result.get("test_scenarios", []))
    }
