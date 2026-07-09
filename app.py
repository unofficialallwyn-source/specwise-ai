"""Streamlit UI for SpecWise AI."""

import logging
from time import perf_counter

import streamlit as st

from src.app_logging import get_logger, log_event
from src.config import get_config
from src.exceptions import SpecWiseError
from src.llm_config import validate_runtime_config

logger = get_logger(__name__)

st.set_page_config(
    page_title="SpecWise AI",
    page_icon="🧠",
    layout="wide",
)

SAMPLE_REQUIREMENTS = {
    "Appointment booking": "Build an online appointment booking system where customers can search available slots, book appointments, receive confirmation, and admins can manage availability.",
    "Expense approval": "Create an employee expense approval workflow where employees submit claims with receipts, managers approve or reject them, and finance tracks reimbursement status.",
    "Learning platform": "Develop a learning platform where students can enroll in courses, watch lessons, take quizzes, and instructors can manage course content and view progress reports.",
}


def format_list(items):
    """Convert list values into markdown bullet points."""
    if not items:
        return "- Not identified."

    return "\n".join([f"- {item}" for item in items])


def initialize_session_state() -> None:
    """Initialize UI session values."""
    if "raw_requirement_input" not in st.session_state:
        st.session_state["raw_requirement_input"] = ""


def load_sample_requirement(sample_name: str) -> None:
    """Load a sample requirement into the text area."""
    st.session_state["raw_requirement_input"] = SAMPLE_REQUIREMENTS[sample_name]
    st.session_state.pop("specwise_result", None)
    st.session_state.pop("token_report", None)
    st.session_state.pop("execution_duration_ms", None)
    log_event(logger, "sample_requirement_loaded", sample_name=sample_name)


def clear_all() -> None:
    """Clear the input and any generated output."""
    st.session_state["raw_requirement_input"] = ""
    st.session_state.pop("specwise_result", None)
    st.session_state.pop("token_report", None)
    st.session_state.pop("execution_duration_ms", None)
    log_event(logger, "ui_input_and_result_cleared")


def clear_result() -> None:
    """Clear only the generated output."""
    st.session_state.pop("specwise_result", None)
    st.session_state.pop("token_report", None)
    st.session_state.pop("execution_duration_ms", None)
    log_event(logger, "ui_result_cleared")


def run_specwise_graph(raw_requirement):
    """Run the SpecWise AI LangGraph workflow."""
    from src.graph_builder import specwise_app
    from src.token_logger import clear_token_usage, get_token_report

    validate_runtime_config()
    clear_token_usage()

    start_time = perf_counter()
    log_event(logger, "specwise_request_received", character_count=len(raw_requirement))

    result = specwise_app.invoke(
        {
            "raw_requirement": raw_requirement,
        }
    )

    token_report = get_token_report()
    duration_ms = round((perf_counter() - start_time) * 1000, 2)

    log_event(
        logger,
        "specwise_request_completed",
        duration_ms=duration_ms,
        node_count=len(token_report),
        total_tokens=sum(item.get("total_tokens", 0) for item in token_report),
    )

    return result, token_report, duration_ms


def render_configuration_summary() -> None:
    """Show current runtime configuration in the sidebar."""
    config = get_config()

    st.sidebar.subheader("Runtime configuration")
    st.sidebar.caption("Loaded from environment variables, `.env`, or `config/specwise.properties`.")

    st.sidebar.metric("Provider", config.llm_provider)
    st.sidebar.metric("Model", config.model_name)
    st.sidebar.metric("Temperature", config.temperature)
    st.sidebar.metric("Max retries", config.llm_max_retries)
    st.sidebar.metric("Timeout", f"{config.llm_timeout_seconds}s")
    st.sidebar.caption(f"API key env: `{config.llm_api_key_env}`")

    if config.llm_base_url:
        st.sidebar.caption(f"Base URL: `{config.llm_base_url}`")

    with st.sidebar.expander("Output limits"):
        st.write(f"Functional requirements: {config.max_functional_requirements}")
        st.write(f"Non-functional requirements: {config.max_non_functional_requirements}")
        st.write(f"Roles: {config.max_roles}")
        st.write(f"Epics: {config.max_epics}")
        st.write(f"User stories: {config.max_user_stories}")
        st.write(f"Acceptance criteria: {config.max_acceptance_criteria}")
        st.write(f"Open questions: {config.max_open_questions}")
        st.write(f"Assumptions: {config.max_assumptions}")
        st.write(f"Risks: {config.max_risks}")
        st.write(f"Dependencies: {config.max_dependencies}")
        st.write(f"Test scenarios: {config.max_test_scenarios}")


def render_empty_state() -> None:
    """Show a helpful empty state before the first generation."""
    st.info("Start by typing a rough requirement or loading one of the examples above.")

    col_1, col_2, col_3 = st.columns(3)
    with col_1:
        st.markdown("**1. Paste requirement**")
        st.caption("Use plain English. Incomplete client notes are fine.")
    with col_2:
        st.markdown("**2. Generate document**")
        st.caption("SpecWise AI runs the LangGraph workflow node by node.")
    with col_3:
        st.markdown("**3. Review and download**")
        st.caption("Use the output as a Product Owner first draft.")


def render_result_summary(result, token_report, execution_duration_ms) -> None:
    """Show high-level result metrics."""
    total_tokens = sum(item.get("total_tokens", 0) for item in token_report)

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("User stories", len(result.get("user_stories", [])))
    metric_2.metric("Acceptance criteria", len(result.get("acceptance_criteria", [])))
    metric_3.metric("Open questions", len(result.get("open_questions", [])))
    metric_4.metric("Total tokens", total_tokens)

    if execution_duration_ms is not None:
        st.caption(f"Execution time: {round(execution_duration_ms / 1000, 2)} seconds")


def render_token_usage(token_report) -> None:
    """Render token usage in a cleaner format."""
    st.subheader("Token Usage")

    if not token_report:
        st.info("No token usage data available yet.")
        return

    total_input_tokens = sum(item.get("input_tokens", 0) for item in token_report)
    total_output_tokens = sum(item.get("output_tokens", 0) for item in token_report)
    total_tokens = sum(item.get("total_tokens", 0) for item in token_report)
    total_cached_tokens = sum(item.get("cached_tokens", 0) for item in token_report)

    metric_col_1, metric_col_2, metric_col_3, metric_col_4 = st.columns(4)
    metric_col_1.metric("Input tokens", total_input_tokens)
    metric_col_2.metric("Output tokens", total_output_tokens)
    metric_col_3.metric("Total tokens", total_tokens)
    metric_col_4.metric("Cached tokens", total_cached_tokens)

    st.dataframe(token_report, use_container_width=True, hide_index=True)

    with st.expander("How to read this"):
        st.markdown(
            """
            - **Input tokens**: prompt/context sent to the model.
            - **Output tokens**: response generated by the model.
            - **Total tokens**: input + output tokens.
            - **Cached tokens**: tokens reused by the provider when available.
            """
        )


def render_result_tabs(result, token_report, execution_duration_ms) -> None:
    """Render generated result tabs."""
    final_output = result.get("final_output", "")

    render_result_summary(result, token_report, execution_duration_ms)

    tab_final, tab_stories, tab_ac, tab_questions, tab_risks, tab_tests, tab_tokens, tab_download = st.tabs(
        [
            "Final PO Document",
            "User Stories",
            "Acceptance Criteria",
            "Open Questions",
            "Risks & Assumptions",
            "Test Scenarios",
            "Token Usage",
            "Download",
        ]
    )

    with tab_final:
        st.subheader("Final PO Document")
        if final_output:
            st.markdown(final_output)
        else:
            st.warning("The graph completed, but no final output was produced.")

    with tab_stories:
        st.subheader("User Stories")
        st.markdown(format_list(result.get("user_stories", [])))

    with tab_ac:
        st.subheader("Acceptance Criteria")
        st.markdown(format_list(result.get("acceptance_criteria", [])))

    with tab_questions:
        st.subheader("Open Questions")
        st.markdown(format_list(result.get("open_questions", [])))

    with tab_risks:
        col_risks, col_assumptions, col_dependencies = st.columns(3)

        with col_risks:
            st.subheader("Risks")
            st.markdown(format_list(result.get("risks", [])))

        with col_assumptions:
            st.subheader("Assumptions")
            st.markdown(format_list(result.get("assumptions", [])))

        with col_dependencies:
            st.subheader("Dependencies")
            st.markdown(format_list(result.get("dependencies", [])))

    with tab_tests:
        st.subheader("Test Scenarios")
        st.markdown(format_list(result.get("test_scenarios", [])))

    with tab_tokens:
        render_token_usage(token_report)

    with tab_download:
        st.subheader("Download Markdown")
        st.caption("Download the final Product Owner document as a Markdown file.")
        st.download_button(
            label="Download PO Document",
            data=final_output,
            file_name="specwise-ai-output.md",
            mime="text/markdown",
            disabled=not bool(final_output),
        )


initialize_session_state()

st.title("SpecWise AI")
st.caption("Requirement-to-user-story copilot for Product Owners and Business Analysts")

with st.sidebar:
    st.header("How to use")
    st.markdown(
        """
        1. Paste a rough client requirement.
        2. Click **Generate PO Document**.
        3. Review the generated artifacts.
        4. Download the final output as Markdown.
        """
    )

    st.divider()
    st.info("Keep the input specific for better Product Owner-ready output.")
    st.divider()

render_configuration_summary()

st.markdown("### Start with a sample")
sample_col_1, sample_col_2, sample_col_3 = st.columns(3)

with sample_col_1:
    st.button("Appointment booking", on_click=load_sample_requirement, args=("Appointment booking",))
with sample_col_2:
    st.button("Expense approval", on_click=load_sample_requirement, args=("Expense approval",))
with sample_col_3:
    st.button("Learning platform", on_click=load_sample_requirement, args=("Learning platform",))

st.markdown("### Requirement input")
raw_requirement = st.text_area(
    "Paste rough requirement",
    key="raw_requirement_input",
    placeholder=SAMPLE_REQUIREMENTS["Appointment booking"],
    height=180,
)

col_generate, col_clear_result, col_clear_all = st.columns([1.2, 1, 4])

with col_generate:
    generate_clicked = st.button("Generate PO Document", type="primary")

with col_clear_result:
    st.button("Clear Result", on_click=clear_result)

with col_clear_all:
    st.button("Clear All", on_click=clear_all)

if generate_clicked:
    if raw_requirement.strip() == "":
        st.warning("Please enter a requirement before generating the document.")
    else:
        try:
            with st.status("Generating Product Owner-ready output...", expanded=True) as status:
                status.write("Validating runtime configuration...")
                validate_runtime_config()

                status.write("Running LangGraph workflow...")
                result, token_report, execution_duration_ms = run_specwise_graph(raw_requirement.strip())

                status.write("Preparing UI output...")
                st.session_state["specwise_result"] = result
                st.session_state["token_report"] = token_report
                st.session_state["execution_duration_ms"] = execution_duration_ms

                status.update(label="SpecWise AI output generated successfully.", state="complete", expanded=False)

            st.success("SpecWise AI output generated successfully.")
        except SpecWiseError as error:
            log_event(
                logger,
                "specwise_user_safe_error",
                level=logging.WARNING,
                error_type=type(error).__name__,
                error_message=str(error),
            )
            st.error(error.user_message)

            with st.expander("Technical details"):
                st.code(str(error))
        except Exception as error:
            log_event(
                logger,
                "specwise_unexpected_error",
                level=logging.ERROR,
                error_type=type(error).__name__,
                error_message=str(error),
            )
            st.error(
                "An unexpected error occurred while generating the document. "
                "Please try again. If it continues, check the terminal logs."
            )

            with st.expander("Technical details"):
                st.exception(error)

result = st.session_state.get("specwise_result")
token_report = st.session_state.get("token_report", [])
execution_duration_ms = st.session_state.get("execution_duration_ms")

st.divider()

if result:
    render_result_tabs(result, token_report, execution_duration_ms)
else:
    render_empty_state()

st.divider()
st.caption("SpecWise AI · Requirement-to-User-Story Copilot · Built with Streamlit, LangGraph, LangChain, and OpenAI")
