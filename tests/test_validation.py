"""Tests for SpecWise AI output validation."""

from src.formatter import final_output_formatter
from src.validation import validate_specwise_result


def build_valid_state():
    state = {
        "raw_requirement": "Build booking feature",
        "feature_summary": "A booking feature.",
        "identified_roles": ["customer"],
        "functional_requirements": ["Search slots"],
        "non_functional_requirements": ["Fast response"],
        "epics": ["Booking Management"],
        "user_stories": ["As a customer, I want to book a slot so that I can reserve time."],
        "acceptance_criteria": ["Given slots exist, when I search, then available slots are shown."],
        "open_questions": ["Should users cancel bookings?"],
        "assumptions": ["Users have accounts."],
        "risks": ["Slot conflicts may occur."],
        "test_scenarios": ["Search available slots"],
        "dependencies": ["Calendar service"],
    }
    state.update(final_output_formatter(state))
    return state


def test_validate_specwise_result_passes_for_valid_result():
    result = build_valid_state()
    validation = validate_specwise_result(
        specwise_result=result,
        sample_input_state={"raw_requirement": "Build booking feature"},
        forbidden_terms=[],
    )

    assert validation["fields_valid"] is True
    assert validation["raw_requirement_valid"] is True
    assert validation["sections_valid"] is True
    assert validation["content_valid"] is True


def test_validate_specwise_result_reports_missing_fields():
    result = build_valid_state()
    result.pop("epics")

    validation = validate_specwise_result(
        specwise_result=result,
        sample_input_state={"raw_requirement": "Build booking feature"},
        forbidden_terms=[],
    )

    assert validation["fields_valid"] is False
    assert "epics" in validation["missing_fields"]


def test_validate_specwise_result_detects_raw_requirement_change():
    result = build_valid_state()
    result["raw_requirement"] = "Changed requirement"

    validation = validate_specwise_result(
        specwise_result=result,
        sample_input_state={"raw_requirement": "Build booking feature"},
        forbidden_terms=[],
    )

    assert validation["raw_requirement_valid"] is False


def test_validate_specwise_result_detects_forbidden_terms():
    result = build_valid_state()
    result["final_output"] += "\nForbiddenVendor"

    validation = validate_specwise_result(
        specwise_result=result,
        sample_input_state={"raw_requirement": "Build booking feature"},
        forbidden_terms=["ForbiddenVendor"],
    )

    assert validation["content_valid"] is False
    assert validation["found_forbidden_terms"] == ["ForbiddenVendor"]
