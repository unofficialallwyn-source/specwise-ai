# Deployment Guide

This guide explains how to prepare and deploy SpecWise AI.

## Recommended deployment target

For the MVP, Streamlit Community Cloud is the simplest deployment target because the application is already built with Streamlit.

## Pre-deployment checklist

Before deploying, verify these items:

- The app runs locally or in GitHub Codespaces.
- `python -m pip install -r requirements.txt` completes successfully.
- `pytest` passes.
- The repository contains `.streamlit/config.toml`.
- The repository contains `config/specwise.properties` for non-secret runtime settings.
- Secret values are not committed to GitHub.
- The deployment platform has the OpenAI API key configured as a secret.

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

6. Add the OpenAI API key in the platform's secret settings.
7. Deploy the app.

## Runtime configuration

Non-secret settings are stored in:

```text
config/specwise.properties
```

Example settings:

```properties
SPECWISE_MODEL=gpt-4o
SPECWISE_TEMPERATURE=0.0
SPECWISE_MAX_USER_STORIES=5
```

Secret settings must be configured in the deployment platform, not in source control.

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

Check that the deployment platform secret is configured correctly and that the app has been restarted after adding the secret.

### App fails during generation

Check the runtime logs. SpecWise AI logs structured events for request start, node execution, token usage, and errors.

### Config changes are not reflected

Restart the app after changing `config/specwise.properties`, because runtime config is cached during the process lifecycle.
