"""Validation helpers for SpecWise AI output."""

from typing import Any, Dict, List

from src.app_logging import get_logger, log_event

logger = get_logger(__name__)


def validate_specwise_result(
    specwise_result: Dict[str, Any],
    sample_input_state: Dict[str, Any],
    forbidden_terms: List[str],
) -> Dict[str, Any]:
    fields_valid = True
    raw_requirement_valid = True
    sections_valid = True
    content_valid = True

    expected_fields = [
        "raw_requirement",
        "feature_summary",
        "identified_roles",
        "functional_requirements",
        "non_functional_requirements",
        "epics",
        "user_stories",
        "acceptance_criteria",
        "open_questions",
        "assumptions",
        "risks",
        "test_scenarios",
        "dependencies",
        "final_output",
    ]

    missing_fields = []

    for field in expected_fields:
        if field not in specwise_result:
            missing_fields.append(field)

    if missing_fields:
        fields_valid = False
        log_event(logger, "validation_missing_fields", missing_fields=missing_fields)
    else:
        log_event(logger, "validation_fields_passed")

    input_requirement = sample_input_state["raw_requirement"]

    if specwise_result.get("raw_requirement", "") == input_requirement:
        log_event(logger, "validation_raw_requirement_passed")
    else:
        raw_requirement_valid = False
        log_event(logger, "validation_raw_requirement_failed")

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

    missing_sections = []
    final_output = specwise_result.get("final_output", "")

    for section in required_sections:
        if section not in final_output:
            missing_sections.append(section)

    if missing_sections:
        sections_valid = False
        log_event(logger, "validation_missing_sections", missing_sections=missing_sections)
    else:
        log_event(logger, "validation_sections_passed")

    found_forbidden_terms = []
    final_output_lower = final_output.lower()

    for term in forbidden_terms:
        if term.lower() in final_output_lower:
            found_forbidden_terms.append(term)

    if found_forbidden_terms:
        content_valid = False
        log_event(logger, "validation_forbidden_terms_found", found_forbidden_terms=found_forbidden_terms)
    else:
        log_event(logger, "validation_content_passed")

    return {
        "fields_valid": fields_valid,
        "missing_fields": missing_fields,
        "raw_requirement_valid": raw_requirement_valid,
        "sections_valid": sections_valid,
        "missing_sections": missing_sections,
        "content_valid": content_valid,
        "found_forbidden_terms": found_forbidden_terms,
    }
