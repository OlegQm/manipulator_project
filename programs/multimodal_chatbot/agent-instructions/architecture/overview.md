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
5. **FastAPI** stores image in Redis (if present) → receives `image_id`
6. **FastAPI** stores user message in Redis
7. **FastAPI** builds LangChain message list from session history; annotates message with `[image_id:...]` and `[session_id:...]` markers (image is NOT embedded in context)
8. **LangGraph agent** receives messages, calls `analyze_image` tool with `session_id` + `image_id`
9. **Tool** fetches base64 image from Redis, sends it to the vision model, returns description
10. **Agent** formulates final response incorporating the tool result
11. **FastAPI** stores assistant response in Redis
12. **FastAPI** returns `ChatResponse` with token stats to client

## Image Handling

Images are **not** embedded in the LLM context directly. Instead:
- The image (base64) is stored in Redis under `session:{uuid}:image:{image_id}`
- The agent message contains only a text reference: `[image_id:...] [session_id:...]`
- The agent decides when to call the `analyze_image` tool, which fetches the image from Redis and passes it to the vision model in an isolated call
- This avoids double-spending tokens and keeps the conversation context lightweight
- Images are automatically deleted when the session is deleted or cleaned up

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
| `session:{uuid}:image:{image_uuid}` | String | Base64-encoded image data |
