# This file will contain the AgentState definition

from typing import List, TypedDict

class AgentState(TypedDict):
  raw_requirement: str
  feature_summary : str
  identified_roles : List[str]
  functional_requirements : List[str]
  non_functional_requirements : List[str]
  epics : List[str]
  user_stories : List[str]
  acceptance_criteria : List[str]
  open_questions : List[str]
  assumptions : List[str]
  risks : List[str]
  test_scenarios : List[str]
  dependencies : List[str]
  final_output : str
