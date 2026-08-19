# ServiceNow AI Service Desk Copilot

An AI-assisted service desk copilot that investigates ServiceNow incidents using Claude, gathers evidence with tool calling, and writes triage recommendations back to ServiceNow only after human approval.

This project does not depend on ServiceNow Now Assist.

## How it works

1. You provide a ServiceNow incident number.
2. The agent fetches the incident and hands it to Claude, which can call tools to gather more evidence:
   - `search_incidents` — find related/similar incidents in ServiceNow
   - `search_knowledge` — search the local troubleshooting knowledge base
3. Once Claude has enough context, it produces a structured recommendation (category, priority, assignment type, confidence, explanation).
4. The recommendation is validated locally, then shown to you for approval.
5. Only after you approve does the copilot write the recommendation back to the incident in ServiceNow. Rejected recommendations never touch ServiceNow.

Every step of the investigation, tool call, and approval decision is written to structured logs.

## Project structure

```
src/
  agent.py              # Agentic investigation loop (Claude + tool calling) and gated write-back
  agent_main.py         # CLI entrypoint: run an investigation and approve/reject the recommendation
  claude_client.py      # Claude API client and recommendation validation
  servicenow_client.py  # ServiceNow REST client (OAuth, incident read/search/update)
  knowledge.py          # Local knowledge base search
  logger.py             # Structured logging setup
data/knowledge/         # Troubleshooting knowledge base (Markdown)
tests/                  # pytest test suite
```

## Requirements

- Python 3.11+
- A ServiceNow instance (e.g. a Personal Developer Instance) with OAuth credentials
- An Anthropic API key

## Setup

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your credentials:

   ```bash
   cp .env.example .env
   ```

   | Variable | Description |
   | --- | --- |
   | `ANTHROPIC_API_KEY` | Claude API key |
   | `SERVICENOW_INSTANCE_URL` | Base URL of your ServiceNow instance |
   | `SERVICENOW_CLIENT_ID` | OAuth client ID for ServiceNow |
   | `SERVICENOW_CLIENT_SECRET` | OAuth client secret for ServiceNow |
   | `AWS_REGION` | AWS region (used by planned Lambda deployment) |

   Never commit `.env` or hard-code credentials — secrets are read from environment variables only.

## Usage

Run the copilot from the project root:

```bash
python -m src.agent_main
```

You'll be prompted for an incident number. The agent will show its investigation steps, print the recommendation, and ask for your approval before writing anything to ServiceNow.

## Tests

```bash
pytest
```

## Development rules

- Never hard-code credentials — use environment variables.
- Use structured logging (`src/logger.py`) instead of print statements for anything that needs to be auditable.
- Validate external API responses before acting on them.
- Handle API failures and timeouts gracefully.
- LLM output must never modify ServiceNow directly without human validation.
- Keep read and write operations separated.

## Roadmap

- RAG over a larger knowledge base with embeddings/vector search
- Automated evaluation of recommendation quality
- AWS Lambda + API Gateway deployment
