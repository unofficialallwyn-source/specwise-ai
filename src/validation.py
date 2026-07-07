# This file will contain the code to validate the final output and check if llm is not hallucinating.

from typing import List, Dict, Any

def validate_specwise_result(
    specwise_result: Dict[str, Any],
    sample_input_state: Dict[str, Any],
    forbidden_terms: List[str]
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
      "final_output"
  ]

  missing_fields = []

  for field in expected_fields:
      if field not in specwise_result:
          missing_fields.append(field)

  if len(missing_fields) == 0:
      fields_valid = True
      print("All expected fields are present.")
  else:
      fields_valid = False
      print("Missing fields:")
      print(missing_fields)


  input_requirement = sample_input_state["raw_requirement"]

  if specwise_result.get("raw_requirement", "") == input_requirement:
      print("raw_requirement matches the input requirement.")
  else:
      raw_requirement_valid = False
      print("raw_requirement does not match the input requirement.")


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
      "Test Scenarios"
  ]

  missing_sections = []

  for section in required_sections:
      if section not in specwise_result["final_output"]:
          missing_sections.append(section)

  if len(missing_sections) == 0:
      print("Final output validation passed.")
  else:
      sections_valid = False
      print("Final output validation failed. Missing sections:")
      print(missing_sections)

  found_forbidden_terms = []

  final_output_lower = specwise_result["final_output"].lower()

  for term in forbidden_terms:
      if term in final_output_lower:
          found_forbidden_terms.append(term)

  if len(found_forbidden_terms) == 0:
      print("Content validation passed. No unrelated features found.")
  else:
      content_valid = False
      print("Content validation warning. Found unrelated terms:")
      print(found_forbidden_terms)
  
  return {
    "fields_valid": fields_valid,
    "missing_fields": missing_fields,
    "raw_requirement_valid": raw_requirement_valid,
    "sections_valid": sections_valid,
    "missing_sections": missing_sections,
    "content_valid": content_valid,
    "found_forbidden_terms": found_forbidden_terms
}
