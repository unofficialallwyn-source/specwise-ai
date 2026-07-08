"""Tests for final output formatting."""

from src.formatter import final_output_formatter, format_list_items


def test_format_list_items_returns_not_identified_for_empty_list():
    assert format_list_items([]) == "- Not identified."


def test_format_list_items_converts_items_to_bullets():
    assert format_list_items(["A", "B"]) == "- A\n- B"


def test_final_output_formatter_contains_required_sections():
    state = {
        "feature_summary": "A booking feature.",
        "functional_requirements": ["Search slots"],
        "non_functional_requirements": ["Fast response"],
        "epics": ["Booking Management"],
        "user_stories": ["As a customer, I want to book a slot so that I can reserve time."],
        "acceptance_criteria": ["Given slots exist, when I search, then available slots are shown."],
        "open_questions": ["Should users cancel bookings?"],
        "assumptions": ["Users have accounts."],
        "risks": ["Slot conflicts may occur."],
        "dependencies": ["Calendar service"],
        "test_scenarios": ["Search available slots"],
    }

    result = final_output_formatter(state)
    final_output = result["final_output"]

    required_sections = [
        "Feature Summary",
        "Functional Requirements",
        "Non-Functional Requirements",
        "Epics",
        "User Stories",
        "Acceptance Criteria",
        "Open Questions",
        "Assumptions",
        "Risks",
        "Dependencies",
        "Test Scenarios",
    ]

    for section in required_sections:
        assert section in final_output

    assert "A booking feature." in final_output
    assert "Search slots" in final_output
