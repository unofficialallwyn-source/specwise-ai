# Deployment Guide

This guide explains how to prepare and deploy SpecWise AI.

## Recommended deployment target

For the MVP, Streamlit Community Cloud is the simplest deployment target because the application is already built with Streamlit.

## Deployment model

SpecWise AI is designed as a bring-your-own-key app.

This means:

- The repository does not include any LLM provider key.
- Each user or deployer provides their own key.
- Non-secret runtime settings are stored in `config/specwise.properties`.
- Secrets are stored in `.env`, Codespaces secrets, or deployment platform secrets.

## Pre-deployment checklist

Before deploying, verify these items:

- The app runs locally or in GitHub Codespaces.
- `python -m pip install -r requirements.txt` completes successfully.
- `pytest` passes.
- The repository contains `.streamlit/config.toml`.
- The repository contains `config/specwise.properties` for non-secret runtime settings.
- The repository contains `.env.example` but not a real `.env` file.
- Secret values are not committed to GitHub.
- The deployment platform has the configured LLM provider key added as a secret.

## Local verification

Run tests:

```bash
pytest
```

Run the Streamlit app:

```bash
python -m streamlit run app.py
```

For GitHub Codespaces:

```bash
python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## Streamlit Community Cloud deployment

1. Push the latest code to GitHub.
2. Go to Streamlit Community Cloud.
3. Create a new app from the GitHub repository.
4. Select branch: `main`.
5. Set the main file path as:

```text
app.py
```

6. Add the configured provider key in the platform's secret settings.
7. Deploy the app.

For the default OpenAI setup, add this in Streamlit secrets:

```toml
OPENAI_API_KEY = "your_provider_key_here"
```

If you changed `SPECWISE_LLM_API_KEY_ENV`, add a secret with that exact name instead.

## Runtime configuration

Non-secret settings are stored in:

```text
config/specwise.properties
```

Example default settings:

```properties
SPECWISE_LLM_PROVIDER=openai
SPECWISE_LLM_API_KEY_ENV=OPENAI_API_KEY
SPECWISE_LLM_BASE_URL=
SPECWISE_MODEL=gpt-4o
SPECWISE_TEMPERATURE=0.0
SPECWISE_MAX_USER_STORIES=5
```

For OpenAI-compatible gateways, use:

```properties
SPECWISE_LLM_PROVIDER=openai_compatible
SPECWISE_LLM_API_KEY_ENV=CUSTOM_LLM_KEY
SPECWISE_LLM_BASE_URL=https://your-provider.example.com/v1
SPECWISE_MODEL=your-model-name
```

Then configure `CUSTOM_LLM_KEY` in your `.env` file or deployment secrets.

See `docs/llm-configuration.md` for full provider configuration details.

## Smoke test after deployment

After deployment, test the following:

1. Open the deployed app URL.
2. Load the `Appointment booking` sample.
3. Click **Generate PO Document**.
4. Confirm the final PO document appears.
5. Confirm user stories and acceptance criteria are visible.
6. Confirm token usage appears.
7. Download the Markdown file.

## Troubleshooting

### App shows missing API key

Check that the secret name matches `SPECWISE_LLM_API_KEY_ENV`. For the default configuration, the secret name is `OPENAI_API_KEY`.

### App says provider is unsupported

Use one of the supported provider values:

```text
openai
openai_compatible
```

### App says base URL is missing

`SPECWISE_LLM_BASE_URL` is required when `SPECWISE_LLM_PROVIDER=openai_compatible`.

### App fails during generation

Check the runtime logs. SpecWise AI logs structured events for request start, node execution, token usage, and errors.

### Config changes are not reflected

Restart the app after changing `config/specwise.properties`, because runtime config is cached during the process lifecycle.
