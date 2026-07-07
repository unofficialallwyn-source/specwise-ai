# SpecWise AI

SpecWise AI is a Requirement-to-User-Story Copilot for Product Owners, Business Analysts, and software teams.

It converts rough client requirements into structured Product Owner-ready output, including feature summaries, functional requirements, non-functional requirements, epics, user stories, acceptance criteria, open questions, assumptions, risks, dependencies, and test scenarios.

---

## Why this project exists

Client inputs often arrive as messy emails, meeting notes, short feature ideas, or incomplete requirement statements. Product Owners and Business Analysts then spend time turning that input into delivery-ready artifacts.

SpecWise AI helps speed up that early analysis step by producing a structured first draft that teams can review, refine, and convert into backlog items.

---

## Core features

- Paste a rough requirement into a Streamlit UI
- Generate a complete Product Owner-ready document
- Extract functional and non-functional requirements
- Identify user roles
- Generate epics and user stories
- Generate acceptance criteria
- Identify open questions, assumptions, risks, and dependencies
- Generate test scenarios
- View token usage by LangGraph node
- Download the final output as Markdown
- Centralized runtime configuration
- Non-secret settings externalized in `config/specwise.properties`
- Secrets kept outside source control in `.env` or environment variables
- Structured application logging
- Friendly error handling for missing API keys, malformed AI responses, and LLM failures

---

## Tech stack

| Area | Technology |
|---|---|
| Language | Python |
| UI | Streamlit |
| Agent workflow | LangGraph |
| LLM integration | LangChain + langchain-openai |
| Model provider | OpenAI |
| Secret config | `.env` / environment variables |
| Non-secret config | `config/specwise.properties` |
| State model | TypedDict |
| Logging | Python logging |

---

## Architecture

```text
Streamlit UI
    |
    v
Compiled LangGraph app
    |
    v
Requirement Intake
    |
    v
Requirement Extractor
    |
    v
Role Identifier
    |
    v
Epic Generator
    |
    v
User Story Generator
    |
    v
Acceptance Criteria Generator
    |
    v
Gap Detector
    |
    v
Risk and Assumption Analyzer
    |
    v
Test Scenario Generator
    |
    v
Final Output Formatter
```

---

## Project structure

```text
specwise-ai/
├── app.py
├── requirements.txt
├── README.md
├── config/
│   └── specwise.properties
└── src/
    ├── app_logging.py
    ├── config.py
    ├── exceptions.py
    ├── formatter.py
    ├── graph_builder.py
    ├── llm_config.py
    ├── nodes.py
    ├── state.py
    ├── token_logger.py
    ├── utils.py
    └── validation.py
```

---

## How the workflow works

1. The user enters a rough requirement in the Streamlit app.
2. `app.py` validates runtime configuration and calls the compiled LangGraph workflow.
3. `requirement_intake` preserves the original requirement.
4. Each LLM node receives only the fields it needs, reducing token usage.
5. Each LLM response is parsed as JSON.
6. Token usage is logged per node.
7. The final formatter converts the graph state into a Product Owner-ready Markdown document.
8. The UI displays the result in tabs and provides a Markdown download.

---

## Production hardening included

### Error handling

SpecWise AI includes custom exception classes for predictable failures:

- `ConfigurationError`
- `LLMInvocationError`
- `LLMResponseParseError`

The Streamlit UI shows user-friendly messages while technical details are logged for debugging.

### Logging

Structured logs are written for important runtime events, including:

- Request received
- Node execution started
- Node execution completed
- Node execution failed
- Token usage recorded
- JSON parse failure
- Validation checks

### Configuration

Runtime configuration is centralized in `src/config.py`.

SpecWise AI now separates configuration into two categories:

| Type | Location | Should be committed? |
|---|---|---:|
| Secrets | `.env` or environment variables | No |
| Non-secret runtime settings | `config/specwise.properties` | Yes |

Configuration is resolved using this priority:

```text
1. Environment variable / .env
2. config/specwise.properties
3. Safe default inside src/config.py
```

This means you can keep normal product settings in `config/specwise.properties`, but override them temporarily from `.env` or Codespaces secrets when needed.

#### Secret configuration

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_api_key_here
```

Do not commit `.env`.

#### Non-secret configuration

Edit `config/specwise.properties` for normal runtime settings:

```properties
SPECWISE_MODEL=gpt-4o
SPECWISE_TEMPERATURE=0.0
SPECWISE_LLM_MAX_RETRIES=2
SPECWISE_LLM_TIMEOUT_SECONDS=60

SPECWISE_MAX_FUNCTIONAL_REQUIREMENTS=5
SPECWISE_MAX_NON_FUNCTIONAL_REQUIREMENTS=5
SPECWISE_MAX_ROLES=4
SPECWISE_MAX_EPICS=3
SPECWISE_MAX_USER_STORIES=5
SPECWISE_MAX_ACCEPTANCE_CRITERIA=5
SPECWISE_MAX_OPEN_QUESTIONS=5
SPECWISE_MAX_ASSUMPTIONS=5
SPECWISE_MAX_RISKS=5
SPECWISE_MAX_DEPENDENCIES=5
SPECWISE_MAX_TEST_SCENARIOS=6
```

You can also point the app to a different properties file using:

```bash
SPECWISE_PROPERTIES_PATH=/path/to/specwise.properties
```

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd specwise-ai
```

### 2. Create a virtual environment

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Add your OpenAI API key

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_api_key_here
```

### 5. Optional: adjust runtime settings

Edit:

```text
config/specwise.properties
```

For example, to generate more user stories, update:

```properties
SPECWISE_MAX_USER_STORIES=8
```

Then restart the Streamlit app so the cached configuration reloads.

### 6. Run the app

```bash
python -m streamlit run app.py
```

For GitHub Codespaces:

```bash
python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

---

## Example input

```text
Build an online appointment booking system where customers can search available slots, book appointments, receive confirmation, and admins can manage availability.
```

---

## Example output sections

SpecWise AI generates a Markdown document with these sections:

1. Feature Summary
2. Functional Requirements
3. Non-Functional Requirements
4. Epics
5. User Stories
6. Acceptance Criteria
7. Open Questions
8. Assumptions
9. Risks
10. Dependencies
11. Test Scenarios

---

## Token optimization strategy

SpecWise AI avoids sending the full state to every LLM call. Each node receives only the fields needed for that task.

Examples:

- `role_identifier` receives feature summary and functional requirements.
- `acceptance_criteria_generator` receives only user stories.
- `test_scenario_generator` receives user stories and acceptance criteria.

This keeps prompts smaller, reduces cost, and makes the workflow easier to debug.

---

## Roadmap

Potential future enhancements:

- Jira export
- Confluence export
- PDF download
- Requirement comparison
- Meeting transcript to PRD
- File upload support
- Multi-language output
- Human review checkpoints
- FastAPI backend
- Authentication for hosted deployments

---

## Portfolio positioning

This project demonstrates:

- AI product thinking
- LangGraph workflow design
- LLM response parsing
- Token optimization
- Streamlit productization
- Runtime configuration management
- Externalized properties configuration
- Structured logging
- Error handling
- GitHub-based development workflow

SpecWise AI is designed as a practical AI Product Owner assistant, not just a simple chatbot demo.
