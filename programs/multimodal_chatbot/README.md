# Multimodal Chatbot

A multimodal chatbot REST API that accepts images and text to answer questions. Built with **FastAPI**, **LangGraph**, and **OpenAI GPT-5-mini**.

## Features

- **Multimodal**: Send images (base64) + text questions, get intelligent answers
- **Session-based**: Per-session chat history stored in Redis
- **Token management**: Tracks token usage with tiktoken, enforces context window limits
- **Auto-cleanup**: Expired sessions (>1h inactivity) automatically purged every 10 minutes
- **Dockerized**: Single `docker compose up` starts all services
- **Secured**: Nginx reverse proxy with HTTP Basic Authentication
- **CI/CD**: GitHub Actions pipeline with automated tests and SSH deployment

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### 1. Configure environment

```bash
cd programs/multimodal_chatbot
cp .env.example .env
# Edit .env with your actual values (API key, auth credentials)
```

### 2. Start the application

```bash
docker compose up -d --build
```

This starts 3 services:
- **app** — FastAPI application on internal port 8000
- **redis** — Redis 7 for session storage
- **nginx** — Reverse proxy on port 80 with basic auth

### 3. Verify

```bash
curl http://localhost/health
# {"status": "ok", "redis": "connected"}
```

## API Usage

All endpoints (except `/health`) require HTTP Basic Auth.

### Create a session

```bash
curl -u admin:password -X POST http://localhost/api/v1/sessions
# {"session_id": "abc-123...", "created_at": "..."}
```

### Send a text message

```bash
curl -u admin:password -X POST http://localhost/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc-123...", "message": "Hello!"}'
```

### Send an image + question

```bash
IMAGE_B64=$(base64 -w0 photo.jpg)
curl -u admin:password -X POST http://localhost/api/v1/chat \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"abc-123...\", \"message\": \"What is this?\", \"image\": \"$IMAGE_B64\"}"
```

### Get chat history

```bash
curl -u admin:password http://localhost/api/v1/sessions/abc-123.../history
```

### Delete a session

```bash
curl -u admin:password -X DELETE http://localhost/api/v1/sessions/abc-123...
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | **Required.** OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection string |
| `SESSION_TTL_SECONDS` | `3600` | Session inactivity timeout (seconds) |
| `CLEANUP_INTERVAL_SECONDS` | `600` | Cleanup job interval (seconds) |
| `MAX_CONTEXT_TOKENS` | `100000` | Max tokens per session |
| `BASIC_AUTH_USER` | `admin` | Nginx basic auth username |
| `BASIC_AUTH_PASSWORD` | `changeme` | Nginx basic auth password |
| `LOG_LEVEL` | `INFO` | Python logging level |

## Project Structure

```
programs/multimodal_chatbot/
├── docker-compose.yaml       # Docker services definition
├── pytest.ini                # pytest configuration
├── .env / .env.example       # Environment configuration
├── app/
│   ├── Dockerfile            # App container image
│   ├── requirements.txt      # Runtime Python dependencies
│   ├── main.py               # FastAPI entry point
│   ├── config.py             # Pydantic BaseSettings
│   ├── models/               # Request/response schemas
│   ├── routers/              # API endpoints
│   ├── services/             # Business logic (agent, sessions, cleanup)
│   └── tools/                # LangGraph tools
├── nginx/                    # Nginx config + Dockerfile
├── tests/                    # pytest test suite
│   ├── Dockerfile            # Test runner container image
│   └── requirements.txt      # Test dependencies (references app/requirements.txt)
└── agent-instructions/       # Documentation
```

## Testing

Tests run inside a dedicated Docker container via the `test` profile:

```bash
# Run all tests in Docker (recommended)
cd programs/multimodal_chatbot
docker compose --profile test run --rm tests
```

Each container has its own `requirements.txt`:
- `app/requirements.txt` — runtime dependencies
- `tests/requirements.txt` — test dependencies (references app deps via `-r`)

## Deployment

Push to `main` branch triggers automatic deployment via GitHub Actions:
1. Tests run in CI
2. On success, code is synced to EC2 via SSH
3. Docker Compose rebuilds and restarts services

See [agent-instructions/deployment/server-setup.md](agent-instructions/deployment/server-setup.md) for manual setup.

## Documentation

- [Implementation Plan](agent-instructions/PLAN.md)
- [Architecture Overview](agent-instructions/architecture/overview.md)
- [API Reference](agent-instructions/api/endpoints.md)
- [Deployment Guide](agent-instructions/deployment/server-setup.md)
