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
- Bring-your-own-key LLM configuration
- Configurable LLM provider with `openai` and `openai_compatible` modes
- Centralized runtime configuration
- Non-secret settings externalized in `config/specwise.properties`
- Secrets kept outside source control in `.env` or environment variables
- Structured application logging
- Friendly error handling for missing keys, malformed AI responses, and LLM failures
- Automated tests for deterministic non-LLM modules
- Streamlit deployment configuration
- GitHub Actions workflow for tests

---

## Tech stack

| Area | Technology |
|---|---|
| Language | Python |
| UI | Streamlit |
| Agent workflow | LangGraph |
| LLM integration | LangChain + langchain-openai |
| Default model provider | OpenAI |
| Compatible provider mode | OpenAI-compatible chat endpoints |
| Secret config | `.env` / environment variables / deployment secrets |
| Non-secret config | `config/specwise.properties` |
| Testing | pytest |
| CI | GitHub Actions |
| State model | TypedDict |
| Logging | Python logging |

---

## Architecture

```text
Streamlit UI
    |
    v
Runtime Config + Provider Validation
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

See the detailed architecture notes in [`docs/architecture.md`](docs/architecture.md).

---

## Project structure

```text
specwise-ai/
├── .env.example
├── .github/
│   └── workflows/
│       └── tests.yml
├── .streamlit/
│   └── config.toml
├── app.py
├── config/
│   └── specwise.properties
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   ├── demo-script.md
│   ├── llm-configuration.md
│   └── screenshots/
│       └── placeholder.txt
├── pytest.ini
├── README.md
├── requirements.txt
├── src/
│   ├── app_logging.py
│   ├── config.py
│   ├── exceptions.py
│   ├── formatter.py
│   ├── graph_builder.py
│   ├── llm_config.py
│   ├── nodes.py
│   ├── state.py
│   ├── token_logger.py
│   ├── utils.py
│   └── validation.py
└── tests/
    ├── test_config.py
    ├── test_formatter.py
    ├── test_llm_config.py
    ├── test_token_logger.py
    ├── test_utils.py
    └── test_validation.py
```

---

## Bring your own LLM key

SpecWise AI does not include any provider key. To run the app, clone the repository and provide your own key in `.env`, Codespaces secrets, or your deployment platform's secret settings.

Supported provider modes:

| Provider value | Purpose |
|---|---|
| `openai` | Default OpenAI provider |
| `openai_compatible` | Any OpenAI-compatible chat endpoint with a custom base URL |

Default configuration in `config/specwise.properties`:

```properties
SPECWISE_LLM_PROVIDER=openai
SPECWISE_LLM_API_KEY_ENV=OPENAI_API_KEY
SPECWISE_LLM_BASE_URL=
SPECWISE_MODEL=gpt-4o
```

For OpenAI-compatible providers:

```properties
SPECWISE_LLM_PROVIDER=openai_compatible
SPECWISE_LLM_API_KEY_ENV=CUSTOM_LLM_KEY
SPECWISE_LLM_BASE_URL=https://your-provider.example.com/v1
SPECWISE_MODEL=your-model-name
```

Then configure the matching secret in `.env` or deployment secrets:

```bash
CUSTOM_LLM_KEY=your_provider_key_here
```

See [`docs/llm-configuration.md`](docs/llm-configuration.md) for full configuration details.

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

SpecWise AI separates configuration into two categories:

| Type | Location | Should be committed? |
|---|---|---:|
| Secrets | `.env`, environment variables, or deployment secrets | No |
| Non-secret runtime settings | `config/specwise.properties` | Yes |

Configuration is resolved using this priority:

```text
1. Environment variable / .env
2. config/specwise.properties
3. Safe default inside src/config.py
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

### 4. Configure your provider key

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Then add your own provider key:

```bash
OPENAI_API_KEY=your_provider_key_here
```

Do not commit `.env`.

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

## Testing

Run the automated test suite:

```bash
pytest
```

The tests cover:

- Configuration loading and override priority
- LLM provider validation
- JSON parsing and JSON parse failures
- Final Markdown formatting
- Output validation rules
- Token usage extraction and logging

The tests do not call any live LLM provider.

GitHub Actions runs the test suite on pushes and pull requests to `main`.

---

## Deployment

See [`docs/deployment.md`](docs/deployment.md) for the full deployment guide.

Minimum deployment checklist:

1. Push code to GitHub.
2. Confirm GitHub Actions tests pass.
3. Deploy `app.py` to Streamlit Community Cloud or another hosting platform.
4. Configure the provider key as a deployment secret.
5. Run a smoke test using one of the sample requirements.

Streamlit theme and deployment defaults are configured in:

```text
.streamlit/config.toml
```

---

## Demo and portfolio assets

Use these files to prepare the project for GitHub, LinkedIn, or interviews:

| File | Purpose |
|---|---|
| `docs/architecture.md` | Technical architecture explanation |
| `docs/deployment.md` | Deployment and smoke-test instructions |
| `docs/llm-configuration.md` | Bring-your-own-key provider configuration |
| `docs/demo-script.md` | Demo walkthrough and interview explanation |
| `docs/screenshots/placeholder.txt` | Screenshot checklist |

Recommended public positioning:

```text
Live demo access is restricted to control provider usage. The source code is available for self-hosting with your own LLM key.
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
- Additional native provider integrations

---

## Portfolio positioning

This project demonstrates:

- AI product thinking
- LangGraph workflow design
- LLM response parsing
- Configurable provider architecture
- Bring-your-own-key deployment model
- Token optimization
- Streamlit productization
- Runtime configuration management
- Externalized properties configuration
- Structured logging
- Error handling
- Automated testing
- CI workflow setup
- Deployment readiness
- GitHub-based development workflow

SpecWise AI is designed as a practical AI Product Owner assistant, not just a simple chatbot demo.
