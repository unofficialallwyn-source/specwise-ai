# Convert the final graph state into a clean Product Owner document.

from typing import Any, List
from src.state import AgentState

def format_list_items(items: List[Any]) -> str:
    """
    Converts a list of items into bullet-point text.
    If the list is empty, it returns 'Not identified.'
    """
    if not items:
        return "- Not identified."

    return "\n".join([f"- {item}" for item in items])


def final_output_formatter(spec_state: AgentState) -> dict:
    """
    Formats all generated SpecWise AI outputs into a clean
    Product Owner ready document.
    """

    final_output = f"""
# SpecWise AI Output

## 1. Feature Summary

{spec_state.get("feature_summary", "Not identified.")}

## 2. Functional Requirements

{format_list_items(spec_state.get("functional_requirements", []))}

## 3. Non-Functional Requirements

{format_list_items(spec_state.get("non_functional_requirements", []))}

## 4. Epics

{format_list_items(spec_state.get("epics", []))}

## 5. User Stories

{format_list_items(spec_state.get("user_stories", []))}

## 6. Acceptance Criteria

{format_list_items(spec_state.get("acceptance_criteria", []))}

## 7. Open Questions

{format_list_items(spec_state.get("open_questions", []))}

## 8. Assumptions

{format_list_items(spec_state.get("assumptions", []))}

## 9. Risks

{format_list_items(spec_state.get("risks", []))}

## 10. Dependencies

{format_list_items(spec_state.get("dependencies", []))}

## 11. Test Scenarios

{format_list_items(spec_state.get("test_scenarios", []))}
"""

    return {
        "final_output": final_output
    }
