# Convert the final graph state into a clean Product Owner document.

from state import AgentState

def format_list_items(items):
    """
    Converts a list of items into bullet-point text.
    If the list is empty, it returns 'Not identified.'
    """
    if not items:
        return "- Not identified."

    return "\n".join([f"- {item}" for item in items])


def final_output_formatter(specState: AgentState):
    """
    Formats all generated SpecWise AI outputs into a clean
    Product Owner ready document.
    """

    final_output = f"""
# SpecWise AI Output

## 1. Feature Summary

{specState.get("feature_summary", "Not identified.")}

## 2. Functional Requirements

{format_list_items(specState.get("functional_requirements", []))}

## 3. Non-Functional Requirements

{format_list_items(specState.get("non_functional_requirements", []))}

## 4. Epics

{format_list_items(specState.get("epics", []))}

## 5. User Stories

{format_list_items(specState.get("user_stories", []))}

## 6. Acceptance Criteria

{format_list_items(specState.get("acceptance_criteria", []))}

## 7. Open Questions

{format_list_items(specState.get("open_questions", []))}

## 8. Assumptions

{format_list_items(specState.get("assumptions", []))}

## 9. Risks

{format_list_items(specState.get("risks", []))}

## 10. Dependencies

{format_list_items(specState.get("dependencies", []))}

## 11. Test Scenarios

{format_list_items(specState.get("test_scenarios", []))}
"""

    return {
        "final_output": final_output
    }
