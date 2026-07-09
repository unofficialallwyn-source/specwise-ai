# LLM Configuration Guide

SpecWise AI is designed as a bring-your-own-key application. The repository does not include any provider API key.

Users can clone the project, provide their own key, and run the app locally or deploy it to their own environment.

## Supported providers

| Provider value | Purpose |
|---|---|
| `openai` | Default OpenAI provider using `langchain-openai` |
| `openai_compatible` | Any OpenAI-compatible chat completions gateway with a custom base URL |

The app uses `ChatOpenAI` from `langchain-openai` for both modes. The `openai_compatible` mode is useful for providers or gateways that expose an OpenAI-compatible API.

## Configuration priority

Values are resolved in this order:

```text
1. Environment variable / .env
2. config/specwise.properties
3. Safe defaults in src/config.py
```

## Default OpenAI setup

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Then add your own provider key:

```bash
OPENAI_API_KEY=your_provider_key_here
```

Use this configuration in `config/specwise.properties`:

```properties
SPECWISE_LLM_PROVIDER=openai
SPECWISE_LLM_API_KEY_ENV=OPENAI_API_KEY
SPECWISE_LLM_BASE_URL=
SPECWISE_MODEL=gpt-4o
```

## OpenAI-compatible setup

Use this when your provider exposes an OpenAI-compatible chat completions endpoint.

Example:

```properties
SPECWISE_LLM_PROVIDER=openai_compatible
SPECWISE_LLM_API_KEY_ENV=CUSTOM_LLM_KEY
SPECWISE_LLM_BASE_URL=https://your-provider.example.com/v1
SPECWISE_MODEL=your-model-name
```

Then add the matching secret to `.env` or your deployment platform:

```bash
CUSTOM_LLM_KEY=your_provider_key_here
```

## Streamlit Community Cloud secrets

In Streamlit Community Cloud, add the same key name configured in `SPECWISE_LLM_API_KEY_ENV`.

For the default OpenAI setup:

```toml
OPENAI_API_KEY = "your_provider_key_here"
```

For a custom provider key name:

```toml
CUSTOM_LLM_KEY = "your_provider_key_here"
```

## Public sharing recommendation

For public GitHub or LinkedIn sharing, do not expose a live app that uses your private provider key unless you are comfortable paying for all usage.

Recommended public positioning:

```text
Live demo access is restricted to control provider usage. The source code is available for self-hosting with your own LLM key.
```

## Important notes

- Do not commit `.env`.
- Do not put real keys in `config/specwise.properties`.
- Restart the app after changing provider settings because runtime config is cached.
- Output quality can vary significantly between providers and models.
