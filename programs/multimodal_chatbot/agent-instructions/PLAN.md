# Multimodal Chatbot — Implementation Plan

> **Status**: Implementation complete. All 27 tests passing. Docker Compose verified locally.  
> **Last updated**: 2026-03-08

---

## TL;DR

Build a multimodal chatbot REST API (**FastAPI + LangGraph + OpenAI GPT-5-mini**) that:
- accepts images (base64) + text questions from a mobile app
- stores per-session chat history in **Redis**
- auto-cleans up expired sessions (cron every 10 min, 1h TTL)
- checks token limits via `tiktoken` (HTTP 409 if context window exceeded)
- runs in **Docker** with **Nginx basic auth** in front
- deploys to AWS EC2 via **GitHub Actions** CI/CD

---

## Decisions

| Concern | Decision |
|---------|----------|
| LLM | OpenAI GPT-5-mini (multimodal: vision + text) |
| Agent framework | LangGraph `StateGraph` (full agent, not a plain API call) |
| Agent tools (v1) | `analyze_image` — vision tool (expandable later) |
| API interface | REST only |
| Session storage | Redis (sessions survive restarts until TTL expires) |
| Session lifecycle | Created via endpoint; deleted via endpoint **or** auto-cleanup |
| Session TTL | 1 hour of inactivity |
| Cleanup interval | Every 10 minutes |
| Token limit | tiktoken; HTTP 409 if exceeded → client must recreate chat |
| Auth | Nginx basic auth, credentials in `.env` / GitHub Secrets |
| TLS / DNS | Not required — plain HTTP only |

---

## Target Project Structure

```
programs/multimodal_chatbot/
├── docker-compose.yaml              # top-level, single 'docker compose up' command
├── pytest.ini                       # pytest configuration
├── .env                             # secrets (never committed)
├── .env.example                     # template with placeholder values
├── README.md                        # project overview + quick start
│
├── agent-instructions/
│   ├── PLAN.md                      # ← this file
│   ├── architecture/
│   │   └── overview.md              # tech stack, data flow diagram
│   ├── api/
│   │   └── endpoints.md             # full API reference with examples
│   └── deployment/
│       └── server-setup.md          # EC2 setup, GitHub Secrets, deployment guide
│
├── app/
│   ├── Dockerfile                   # Python 3.12-slim app image
│   ├── requirements.txt             # runtime Python dependencies
│   ├── __init__.py
│   ├── main.py                      # FastAPI app, lifespan, middleware, router mount
│   ├── config.py                    # Pydantic BaseSettings (all env vars)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chat.py                  # ChatRequest, ChatResponse, TokenLimitError
│   │   └── session.py               # SessionCreate, SessionResponse, SessionDeleteResponse
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── chat.py                  # POST /api/v1/chat
│   │   ├── session.py               # CRUD /api/v1/sessions
│   │   └── health.py                # GET /health
│   ├── services/
│   │   ├── __init__.py
│   │   ├── agent.py                 # LangGraph StateGraph agent
│   │   ├── session_manager.py       # Redis session CRUD + tiktoken token counting
│   │   └── cleanup.py               # APScheduler background cleanup task
│   └── tools/
│       ├── __init__.py
│       └── image_analysis.py        # LangGraph @tool: analyze image via vision
│
├── nginx/
│   ├── nginx.conf                   # reverse proxy + basic auth config
│   ├── Dockerfile                   # nginx:alpine + apache2-utils
│   └── entrypoint.sh                # generate .htpasswd from env vars at startup
│
└── tests/
    ├── Dockerfile                   # Python 3.12-slim test runner image
    ├── requirements.txt             # test dependencies (references app/requirements.txt)
    ├── __init__.py
    ├── conftest.py                  # fixtures: fakeredis, async test client
    ├── test_health.py
    ├── test_session.py
    └── test_chat.py
```

---

## Phase 1 — Project Scaffold & Configuration

### Step 1.1 — Directory tree
Create all directories and empty `__init__.py` files listed above.

### Step 1.2 — `app/config.py` (Pydantic BaseSettings)
Environment variables exposed via `Settings`:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | OpenAI secret key |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model name (change to `gpt-5-mini` when available) |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection string |
| `SESSION_TTL_SECONDS` | `3600` | Inactivity TTL for auto-cleanup |
| `CLEANUP_INTERVAL_SECONDS` | `600` | How often to run cleanup (10 min) |
| `MAX_CONTEXT_TOKENS` | `100000` | Model context window limit |
| `BASIC_AUTH_USER` | — | Nginx basic auth username |
| `BASIC_AUTH_PASSWORD` | — | Nginx basic auth password |
| `LOG_LEVEL` | `INFO` | Logging level |

### Step 1.3 — Secrets files
- `.env` — real values (not committed to git)
- `.env.example` — placeholders documenting required variables
- `.gitignore` — ensure `.env` is listed

---

## Phase 2 — Data Models & Session Management

### Step 2.1 — Pydantic models (`app/models/`)

**`chat.py`**:
- `ChatRequest`: `session_id: str`, `message: str`, `image: Optional[str]` (base64), `image_url: Optional[str]`
- `ChatResponse`: `session_id: str`, `response: str`, `tokens_used: int`, `tokens_remaining: int`
- `TokenLimitExceededResponse`: `session_id: str`, `error: str`, `action: Literal["recreate_session"]`

**`session.py`**:
- `SessionCreateResponse`: `session_id: str`, `created_at: datetime`
- `SessionInfoResponse`: `session_id: str`, `created_at: datetime`, `last_activity: datetime`, `message_count: int`
- `SessionDeleteResponse`: `session_id: str`, `deleted: bool`
- `ChatMessageRecord`: `role: str`, `content: str`, `has_image: bool`, `image_id: Optional[str]`, `timestamp: datetime`

### Step 2.2 — Redis session service (`app/services/session_manager.py`)

Redis key schema:
- `session:{id}:meta` — hash: `created_at`, `last_activity`
- `session:{id}:messages` — list of JSON-serialized message objects

Methods:
- `create_session() -> str` — generate UUID4, store meta hash
- `session_exists(session_id) -> bool`
- `get_session_info(session_id) -> SessionInfoResponse`
- `add_message(session_id, role, content, has_image=False, image_id=None) -> None` — append to list, update `last_activity`
- `get_history(session_id) -> list[ChatMessageRecord]`
- `store_image(session_id, image_b64) -> str` — store image in Redis and return `image_id`
- `get_image(session_id, image_id) -> Optional[str]`
- `count_tokens(session_id) -> int` — tiktoken encode full conversation
- `check_token_limit(session_id) -> bool` — True if within `MAX_CONTEXT_TOKENS`
- `delete_session(session_id) -> bool`
- `get_all_session_ids() -> list[str]` — for cleanup scanning

### Step 2.3 — Cleanup task (`app/services/cleanup.py`)
- Uses `apscheduler` `AsyncIOScheduler` started in FastAPI lifespan
- Job runs every `CLEANUP_INTERVAL_SECONDS`
- Scans all sessions, deletes those where `now - last_activity > SESSION_TTL_SECONDS`
- Logs number of cleaned sessions

---

## Phase 3 — LangGraph Agent *(parallel with Phase 2)*

### Step 3.1 — Image analysis tool (`app/tools/image_analysis.py`)
```python
@tool
def analyze_image(image_base64: str, question: str) -> str:
    """Analyze an image and answer a specific question about it."""
```
- Constructs a vision-enabled OpenAI message with base64 image content part
- Returns a descriptive string answer

### Step 3.2 — Agent graph (`app/services/agent.py`)

LangGraph `StateGraph` structure:
```
[user message] → agent node → (tool call?) → tools node → agent node → ... → END
```

State:
```python
class AgentState(TypedDict):
    messages: list[BaseMessage]
```

Flow:
- `agent` node: call `ChatOpenAI` with bound tools
- conditional edge: if last message is `ToolMessage` candidate → route to `tools`, else → `END`
- `tools` node: `ToolNode` from langgraph prebuilt

Public function:
```python
async def invoke_agent(
    settings: Settings,
    history: list[ChatMessageRecord],
    user_message: str,
    session_id: str,
    image_id: Optional[str] = None,
    image_url: Optional[str] = None,
) -> str
```

---

## Phase 4 — API Routers *(depends on Phase 2 + 3)*

### `GET /health`
Returns:
```json
{"status": "ok", "redis": "connected"}
```
Returns `503` if Redis is unreachable.

### `POST /api/v1/sessions`
Creates new session. Returns `SessionCreateResponse`.

### `GET /api/v1/sessions/{session_id}`
Returns `SessionInfoResponse` or `404`.

### `GET /api/v1/sessions/{session_id}/history`
Returns list of `ChatMessageRecord` or `404`.

### `DELETE /api/v1/sessions/{session_id}`
Deletes session. Returns `SessionDeleteResponse`.

### `POST /api/v1/chat`
**Request**: `ChatRequest`  
Client sends only `session_id`, current `message`, and optional `image` or `image_url`.
The service loads prior conversation history from Redis by `session_id`; clients do not
send history in the request body.

**Flow**:
1. Validate session exists → `404` if not
2. Check token limit → `409 TokenLimitExceededResponse` if exceeded
3. Store image in Redis if present
4. Store user message in Redis
5. Load session history from Redis and invoke LangGraph agent with it
6. Store assistant response in Redis
7. Return `ChatResponse` with token stats

---

## Phase 5 — Docker & Nginx *(depends on Phase 4)*

### `app/Dockerfile`
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY app/requirements.txt app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements.txt
COPY app/ app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `nginx/nginx.conf`
- Listen port 80
- `auth_basic` with `/etc/nginx/.htpasswd`
- `proxy_pass http://app:8000`
- `client_max_body_size 20M` (for image uploads)

### `nginx/entrypoint.sh`
```bash
htpasswd -bc /etc/nginx/.htpasswd "$BASIC_AUTH_USER" "$BASIC_AUTH_PASSWORD"
exec nginx -g 'daemon off;'
```

### `docker-compose.yaml`
Four services (tests via `--profile test`):
- **app** — builds from repo root (`dockerfile: app/Dockerfile`), internal port 8000, `env_file: .env`, depends_on redis
- **redis** — `redis:7-alpine`, named volume `redis_data`, internal 6379, healthcheck
- **nginx** — builds from `nginx/`, ports `"80:80"`, env `BASIC_AUTH_USER` + `BASIC_AUTH_PASSWORD`, depends_on app
- **tests** — builds from repo root (`dockerfile: tests/Dockerfile`), own `tests/requirements.txt`, profile `test`, depends_on redis

---

## Phase 6 — Testing *(depends on Phase 5)*

Tests run inside a dedicated Docker container (`tests` service with `--profile test`).  
Each container has its own `requirements.txt`:
- `app/requirements.txt` — runtime dependencies
- `tests/requirements.txt` — test dependencies, references `app/requirements.txt` via `-r`

Run tests: `docker compose --profile test run --rm tests`

### `tests/conftest.py`
- `fakeredis` async server fixture replacing real Redis
- `AsyncClient` fixture for FastAPI test client

### Test scenarios

| Test | Description |
|------|-------------|
| Health OK | `GET /health` → 200 |
| Health Redis down | Redis unavailable → 503 |
| Create session | `POST /api/v1/sessions` → 201, return `session_id` |
| Get session | `GET /api/v1/sessions/{id}` → 200 |
| Delete session | `DELETE /api/v1/sessions/{id}` → 200; subsequent GET → 404 |
| Chat text-only | `POST /api/v1/chat` with message only → 200, non-empty response |
| Chat with image | `POST /api/v1/chat` with base64 image → 200, image-related response |
| Token limit | Simulate full context → 409 with `action: "recreate_session"` |
| Cleanup task | Inject expired session, run cleanup, verify deleted |

---

## Phase 7 — CI/CD & Deployment *(depends on Phase 6)*

### `.github/workflows/deploy.yml`

```
Trigger: push to main (paths: programs/multimodal_chatbot/**)

Jobs:
  test:
    - Spin up Redis service container
    - Install dependencies
    - Run pytest

  deploy (needs: test):
    - SSH to 35.156.245.59 (ubuntu)
    - cd /home/ubuntu/multimodal_chatbot
    - git pull
    - Write .env from GitHub Secrets
    - docker compose down && docker compose up -d --build
```

### Required GitHub Secrets

| Secret | Value source |
|--------|-------------|
| `OPENAI_API_KEY` | OpenAI dashboard |
| `BASIC_AUTH_USER` | From `.env` |
| `BASIC_AUTH_PASSWORD` | From `.env` |
| `SSH_PRIVATE_KEY` | Contents of `/home/olegqm/aws_ssh_keys/robotic-arm-chatbot/robotic-arm-ssh-key.pem` |
| `SERVER_HOST` | `35.156.245.59` |
| `SERVER_USER` | `ubuntu` |

---

## Phase 8 — Documentation *(finalized last)*

- `agent-instructions/architecture/overview.md` — architecture diagram + data flow
- `agent-instructions/api/endpoints.md` — full API reference
- `agent-instructions/deployment/server-setup.md` — EC2 prerequisites + step-by-step deploy
- `README.md` — project overview, quick start, env vars table, example API calls

---

## Implementation Order

```
Phase 1 (scaffold, config)
    ↓
Phase 2 (models, Redis service) ──── [parallel] ──── Phase 3 (LangGraph agent)
    ↓                                                      ↓
    └──────────────── Phase 4 (API routers) ───────────────┘
                            ↓
                     Phase 5 (Docker, Nginx)
                            ↓
                      Phase 6 (tests)
                            ↓
                    Phase 7 (CI/CD, deploy)
                            ↓
                  Phase 8 (docs finalize)
```

---

## Final Verification Checklist

- [ ] `docker compose --profile test run --rm tests` — all 27 tests pass in container
- [ ] `docker compose up --build` — all 3 services start without errors
- [ ] `curl -u <user>:<pass> http://localhost/health` → `{"status":"ok","redis":"connected"}`
- [ ] Create session → chat (text) → chat (image+text) → get history → delete session
- [ ] Fill context → receive HTTP 409 with `"action": "recreate_session"`
- [ ] Push to `main` → GitHub Action passes → SSH deploy succeeds
- [ ] `curl -u <user>:<pass> http://35.156.245.59/health` → 200 OK
