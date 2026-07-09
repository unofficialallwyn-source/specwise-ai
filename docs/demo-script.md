# SpecWise AI Demo Script

Use this script for a GitHub README video, LinkedIn demo, or interview walkthrough.

## 30-second elevator pitch

SpecWise AI is a Product Owner assistant that converts rough client requirements into structured delivery-ready artifacts such as feature summaries, functional requirements, epics, user stories, acceptance criteria, open questions, risks, dependencies, and test scenarios.

It is built with Streamlit, LangGraph, LangChain, and OpenAI-compatible LLM configuration, with production-style configuration, logging, error handling, token tracking, tests, and a bring-your-own-key deployment model.

## 2-minute demo flow

### 1. Open the app

Say:

> This is SpecWise AI, a Requirement-to-User-Story Copilot for Product Owners and Business Analysts.

Show:

- Streamlit landing page
- Sidebar runtime configuration
- Configured LLM provider and model
- Sample requirement buttons

### 2. Load a sample requirement

Click:

```text
Appointment booking
```

Say:

> I can start from a rough requirement. It does not need to be a full PRD. The tool is designed for early-stage client notes or business ideas.

### 3. Generate the PO document

Click:

```text
Generate PO Document
```

Say:

> Behind the scenes, a LangGraph workflow runs several specialized nodes. Each node performs one focused task, such as requirement extraction, role identification, user story generation, gap detection, and risk analysis.

Show:

- Status messages
- Final PO Document tab

### 4. Review generated artifacts

Open tabs:

- User Stories
- Acceptance Criteria
- Open Questions
- Risks & Assumptions
- Test Scenarios

Say:

> The output is not meant to replace the Product Owner. It creates a structured first draft that can be reviewed, refined, and converted into backlog items.

### 5. Show token usage

Open:

```text
Token Usage
```

Say:

> Each LLM node logs token usage separately. This helps track cost and understand which parts of the workflow consume the most tokens.

### 6. Download output

Open:

```text
Download
```

Say:

> The final output can be downloaded as Markdown and used in tools like Jira, Confluence, GitHub, or documentation workflows.

## Technical explanation for interviews

### Architecture

> The application uses Streamlit for the UI and LangGraph for orchestration. Each node is responsible for a specific Product Owner task. The graph state is gradually enriched and finally formatted into a Markdown document.

### LLM configuration

> SpecWise AI is designed as a bring-your-own-key app. The live demo can remain restricted to control provider usage, while the source code can be cloned and self-hosted with the user's own provider key. The app supports a default OpenAI mode and an OpenAI-compatible provider mode using configurable provider, key environment variable, base URL, and model settings.

### Configuration

> Secrets are kept outside source control. Non-secret runtime properties are stored in `config/specwise.properties`. The application resolves configuration using environment variables first, then the properties file, then safe defaults.

### Error handling

> Predictable failures are represented with custom exceptions. The UI shows user-friendly messages, while the logs contain technical details for debugging.

### Logging

> Structured logs are written for request start, node execution, token usage, completion, and failures.

### Testing

> The test suite focuses on deterministic logic such as config loading, LLM provider validation, JSON parsing, formatting, validation, and token logging. It avoids live LLM calls so CI can run without a provider key.

## Demo closing statement

> This project demonstrates practical AI engineering beyond a simple chatbot. It includes workflow orchestration, structured output generation, token observability, configurable provider architecture, runtime configuration, error handling, automated tests, and deployment readiness.

## Public sharing statement

Use this when sharing the project publicly:

> Live demo access is restricted to control provider usage. The source code is available for self-hosting with your own LLM key.
