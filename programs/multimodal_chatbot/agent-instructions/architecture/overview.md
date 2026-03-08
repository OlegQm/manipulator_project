# Architecture Overview

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| API Framework | FastAPI | Async REST API with automatic OpenAPI docs |
| Agent Framework | LangGraph | Stateful agent with tool-calling support |
| LLM | OpenAI GPT-5-mini | Multimodal model (vision + text) |
| Session Storage | Redis | Fast in-memory session/chat history storage |
| Token Counting | tiktoken | Count tokens to enforce context window limits |
| Reverse Proxy | Nginx | Basic auth, request proxying, upload limits |
| Containers | Docker Compose | 4-service stack (app, redis, nginx, tests); Dockerfiles in `app/`, `nginx/`, `tests/` |
| CI/CD | GitHub Actions | Automated testing + SSH deployment |
| Configuration | Pydantic Settings | Type-safe env var management via BaseSettings |

## Data Flow

```
Mobile App
    │
    ▼
┌──────────┐   Basic Auth    ┌──────────────┐   HTTP Proxy   ┌──────────────┐
│  Nginx   │ ──────────────► │  FastAPI App  │ ◄────────────► │    Redis     │
│ (port 80)│                 │ (port 8000)   │                │ (port 6379)  │
└──────────┘                 └──────────────┘                └──────────────┘
                                    │
                                    ▼
                             ┌──────────────┐
                             │  LangGraph   │
                             │    Agent     │
                             │  (GPT-5-mini)│
                             └──────────────┘
```

## Request Flow (POST /api/v1/chat)

1. **Client** sends `session_id`, `message`, optional `image` (base64)
2. **Nginx** validates basic auth → proxies to FastAPI
3. **FastAPI** validates session exists in Redis
4. **FastAPI** checks token count (tiktoken) — returns 409 if limit exceeded
5. **FastAPI** stores user message in Redis
6. **FastAPI** builds LangChain message list from session history
7. **LangGraph agent** receives messages, may invoke `analyze_image` tool
8. **Agent** returns response text
9. **FastAPI** stores assistant response in Redis
10. **FastAPI** returns `ChatResponse` with token stats to client

## Session Lifecycle

```
CREATE SESSION ──► CHAT (repeat) ──► DELETE SESSION
      │                                    │
      │         OR                         │
      │                                    │
      └── AUTO-CLEANUP (cron every 10min) ─┘
          deletes sessions inactive > 1 hour
```

## Redis Key Schema

| Key Pattern | Type | Contents |
|-------------|------|----------|
| `session:{uuid}:meta` | Hash | `created_at`, `last_activity` timestamps |
| `session:{uuid}:messages` | List | JSON-serialized message records |
