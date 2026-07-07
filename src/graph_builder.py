# This file will contains the LangGraph definition

from src.state import AgentState

specwise_graph = StateGraph(AgentState)

specwise_graph.add_node("requirement_intake", requirement_intake)
specwise_graph.add_node("requirement_extractor", requirement_extractor)
specwise_graph.add_node("role_identifier", role_identifier)
specwise_graph.add_node("epic_generator", epic_generator)
specwise_graph.add_node("user_story_generator", user_story_generator)
specwise_graph.add_node("acceptance_criteria_generator", acceptance_criteria_generator)
specwise_graph.add_node("gap_detector", gap_detector)
specwise_graph.add_node("risk_assumption_analyzer", risk_assumption_analyzer)
specwise_graph.add_node("test_scenario_generator", test_scenario_generator)
specwise_graph.add_node("final_output_formatter", final_output_formatter)

specwise_graph.add_edge(START, "requirement_intake")
specwise_graph.add_edge("requirement_intake", "requirement_extractor")
specwise_graph.add_edge("requirement_extractor", "role_identifier")
specwise_graph.add_edge("role_identifier", "epic_generator")
specwise_graph.add_edge("epic_generator", "user_story_generator")
specwise_graph.add_edge("user_story_generator", "acceptance_criteria_generator")
specwise_graph.add_edge("acceptance_criteria_generator", "gap_detector")
specwise_graph.add_edge("gap_detector", "risk_assumption_analyzer")
specwise_graph.add_edge("risk_assumption_analyzer", "test_scenario_generator")
specwise_graph.add_edge("test_scenario_generator", "final_output_formatter")
specwise_graph.add_edge("final_output_formatter", END)

specwise_app = specwise_graph.compile()
