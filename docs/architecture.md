# SpecWise AI Architecture

SpecWise AI is designed as a modular AI workflow application. The goal is to convert rough client requirements into Product Owner-ready delivery artifacts.

## High-level architecture

```text
User
  |
  v
Streamlit UI (`app.py`)
  |
  v
Runtime Config + Validation
  |
  v
Compiled LangGraph Workflow (`src/graph_builder.py`)
  |
  v
LLM Nodes (`src/nodes.py`)
  |
  v
Formatter (`src/formatter.py`)
  |
  v
PO-ready Markdown Output
```

## Main components

| Component | Responsibility |
|---|---|
| `app.py` | Streamlit UI, user input, status messages, tabs, download, friendly error handling |
| `src/config.py` | Loads environment variables, `.env`, properties file values, and defaults |
| `config/specwise.properties` | Non-secret runtime settings such as model, retry count, and output limits |
| `src/llm_config.py` | Validates runtime configuration and creates the ChatOpenAI client |
| `src/graph_builder.py` | Defines the LangGraph node sequence and compiles the app |
| `src/nodes.py` | Contains the LLM and non-LLM node functions |
| `src/utils.py` | JSON parsing, compact JSON serialization, list normalization, state text extraction |
| `src/token_logger.py` | Captures token usage from each LLM node |
| `src/formatter.py` | Converts final graph state into Markdown output |
| `src/validation.py` | Validates generated output structure and content constraints |
| `tests/` | Automated tests for non-LLM logic |

## LangGraph flow

```text
START
  |
  v
requirement_intake
  |
  v
requirement_extractor
  |
  v
role_identifier
  |
  v
epic_generator
  |
  v
user_story_generator
  |
  v
acceptance_criteria_generator
  |
  v
gap_detector
  |
  v
risk_assumption_analyzer
  |
  v
test_scenario_generator
  |
  v
final_output_formatter
  |
  v
END
```

## Configuration flow

```text
Environment variable / .env
        |
        v
config/specwise.properties
        |
        v
safe defaults in src/config.py
        |
        v
AppConfig object
        |
        v
LLM setup + node prompt limits
```

Priority order:

1. Environment variable or `.env`
2. `config/specwise.properties`
3. Safe default inside `src/config.py`

## Error handling flow

```text
App starts generation
  |
  v
validate_runtime_config()
  |
  v
LangGraph node execution
  |
  v
LLM invocation + JSON parsing
  |
  v
Custom exception if predictable failure occurs
  |
  v
Streamlit displays friendly message
  |
  v
Structured logs capture technical details
```

Custom exceptions:

- `ConfigurationError`
- `LLMInvocationError`
- `LLMResponseParseError`

## Token optimization strategy

SpecWise AI does not pass the entire graph state to every LLM node. Each node receives only the fields needed for its task.

Examples:

| Node | Input used |
|---|---|
| `role_identifier` | Feature summary, functional requirements |
| `epic_generator` | Functional requirements, identified roles |
| `acceptance_criteria_generator` | User stories |
| `test_scenario_generator` | User stories, acceptance criteria |

This reduces unnecessary context, improves observability, and keeps token usage easier to explain.

## Testing strategy

The automated tests focus on deterministic non-LLM logic:

- Configuration loading and override priority
- JSON parsing and parse failure handling
- Markdown formatting
- Output validation
- Token usage extraction

The test suite deliberately avoids live LLM calls so tests can run safely in CI without requiring an API key.

## Deployment architecture

```text
GitHub Repository
  |
  v
GitHub Actions pytest workflow
  |
  v
Streamlit Community Cloud / hosting platform
  |
  v
Runtime secret configured in deployment settings
  |
  v
Live SpecWise AI app
```
