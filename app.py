"""Streamlit UI for SpecWise AI."""

import streamlit as st


st.set_page_config(
    page_title="SpecWise AI",
    page_icon="🧠",
    layout="wide",
)


def format_list(items):
    """Convert list values into markdown bullet points."""
    if not items:
        return "- Not identified."

    return "\n".join([f"- {item}" for item in items])


def run_specwise_graph(raw_requirement):
    """Run the SpecWise AI LangGraph workflow."""
    from src.graph_builder import specwise_app
    from src.token_logger import clear_token_usage, get_token_report

    clear_token_usage()

    result = specwise_app.invoke(
        {
            "raw_requirement": raw_requirement,
        }
    )

    token_report = get_token_report()

    return result, token_report


st.title("SpecWise AI")
st.caption("Requirement-to-user-story copilot for Product Owners and Business Analysts")

with st.sidebar:
    st.header("How to use")
    st.markdown(
        """
        1. Paste a rough client requirement.
        2. Click **Generate PO Document**.
        3. Review the generated user stories, acceptance criteria, risks, and questions.
        4. Download the final output as Markdown.
        """
    )

    st.divider()
    st.info("Keep the input specific for better Product Owner-ready output.")

sample_requirement = """Build an online appointment booking system where customers can search available slots, book appointments, receive confirmation, and admins can manage availability."""

raw_requirement = st.text_area(
    "Paste rough requirement",
    value="",
    placeholder=sample_requirement,
    height=180,
)

col_generate, col_clear = st.columns([1, 4])

with col_generate:
    generate_clicked = st.button("Generate PO Document", type="primary")

with col_clear:
    clear_clicked = st.button("Clear Result")

if clear_clicked:
    st.session_state.pop("specwise_result", None)
    st.session_state.pop("token_report", None)

if generate_clicked:
    if raw_requirement.strip() == "":
        st.warning("Please enter a requirement before generating the document.")
    else:
        with st.spinner("Generating Product Owner-ready output..."):
            try:
                result, token_report = run_specwise_graph(raw_requirement.strip())
                st.session_state["specwise_result"] = result
                st.session_state["token_report"] = token_report
                st.success("SpecWise AI output generated successfully.")
            except Exception as error:
                st.error("Unable to generate output.")
                st.exception(error)

result = st.session_state.get("specwise_result")
token_report = st.session_state.get("token_report", [])

if result:
    final_output = result.get("final_output", "")

    tab_final, tab_stories, tab_ac, tab_questions, tab_risks, tab_tokens, tab_download = st.tabs(
        [
            "Final PO Document",
            "User Stories",
            "Acceptance Criteria",
            "Open Questions",
            "Risks & Assumptions",
            "Token Usage",
            "Download",
        ]
    )

    with tab_final:
        st.markdown(final_output)

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

    with tab_tokens:
        st.subheader("Token Usage")

        if token_report:
            st.dataframe(token_report, use_container_width=True)

            total_prompt_tokens = sum(item.get("prompt_tokens", 0) for item in token_report)
            total_completion_tokens = sum(item.get("completion_tokens", 0) for item in token_report)
            total_tokens = sum(item.get("total_tokens", 0) for item in token_report)

            metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
            metric_col_1.metric("Prompt tokens", total_prompt_tokens)
            metric_col_2.metric("Completion tokens", total_completion_tokens)
            metric_col_3.metric("Total tokens", total_tokens)
        else:
            st.info("No token usage data available yet.")

    with tab_download:
        st.subheader("Download Markdown")
        st.download_button(
            label="Download PO Document",
            data=final_output,
            file_name="specwise-ai-output.md",
            mime="text/markdown",
        )
else:
    st.info("Enter a requirement and click Generate PO Document to start.")
