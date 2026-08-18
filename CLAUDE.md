# ServiceNow AI Service Desk Copilot

## Project Goal

Build an enterprise-style AI service desk copilot integrating:

- ServiceNow PDI
- Claude API
- AWS
- RAG
- tool calling
- human-in-the-loop controls
- automated evaluation

The application must not depend on ServiceNow Now Assist.

## Architecture

ServiceNow PDI
→ REST API
→ AWS API Gateway
→ AWS Lambda
→ Claude
→ ServiceNow

Later versions will add:
- ServiceNow tools
- RAG
- embeddings/vector search
- HITL
- evaluations

## Technology

- Python 3
- Anthropic Claude API
- ServiceNow REST API
- AWS Lambda
- AWS API Gateway
- AWS CloudWatch
- AWS Secrets Manager
- pytest
- GitHub Actions

## Development Rules

- Never hard-code credentials.
- Use environment variables for secrets.
- Add tests for new application logic.
- Prefer small modular functions.
- Use structured logging instead of print statements.
- Validate external API responses.
- Handle API failures and timeouts gracefully.
- Do not allow LLM output to directly modify ServiceNow without validation.
- Keep read and write operations separated.

## Commands

Run tests:

```bash
pytest
