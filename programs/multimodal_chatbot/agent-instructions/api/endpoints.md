# API Reference

Base URL: `http://<host>` (port 80, behind Nginx basic auth)

> **Note**: All endpoints except `/health` require HTTP Basic Authentication.

---

## Health Check

### `GET /health`

**Auth**: Not required

**Response** (200):
```json
{
    "status": "ok",
    "redis": "connected"
}
```

**Response** (503) — Redis unreachable:
```json
{
    "status": "degraded",
    "redis": "error"
}
```

---

## Sessions

### `POST /api/v1/sessions`

Create a new chat session. Must be called before sending any messages.

**Response** (201):
```json
{
    "session_id": "033389ac-f3ff-496a-b2e4-60e32b133fe2",
    "created_at": "2026-03-07T23:25:51.535999Z"
}
```

---

### `GET /api/v1/sessions/{session_id}`

Get metadata for an existing session.

**Response** (200):
```json
{
    "session_id": "033389ac-f3ff-496a-b2e4-60e32b133fe2",
    "created_at": "2026-03-07T23:25:51.535999Z",
    "last_activity": "2026-03-07T23:26:27.641373Z",
    "message_count": 2
}
```

**Response** (404):
```json
{"detail": "Session 033389ac-... not found"}
```

---

### `GET /api/v1/sessions/{session_id}/history`

Retrieve full chat history for a session.

**Response** (200):
```json
[
    {
        "role": "user",
        "content": "Hello!",
        "has_image": false,
        "timestamp": "2026-03-07T23:26:01Z"
    },
    {
        "role": "assistant",
        "content": "Hi! How can I help you?",
        "has_image": false,
        "timestamp": "2026-03-07T23:26:03Z"
    }
]
```

---

### `DELETE /api/v1/sessions/{session_id}`

Delete a session and all its messages.

**Response** (200):
```json
{
    "session_id": "033389ac-f3ff-496a-b2e4-60e32b133fe2",
    "deleted": true
}
```

---

## Chat

### `POST /api/v1/chat`

Send a message (optionally with an image) to the chatbot agent.

**Request Body**:
```json
{
    "session_id": "033389ac-f3ff-496a-b2e4-60e32b133fe2",
    "message": "What objects are in this image?",
    "image": "<base64-encoded-image-data>",
    "image_url": null
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string (UUID) | Yes | Session ID from `POST /api/v1/sessions` |
| `message` | string | Yes | User's text message or question |
| `image` | string (base64) | No | Base64-encoded image (JPEG/PNG) |
| `image_url` | string (URL) | No | Public URL of an image |

> `image` and `image_url` are mutually exclusive. Send at most one.

**Response** (200):
```json
{
    "session_id": "033389ac-f3ff-496a-b2e4-60e32b133fe2",
    "response": "I can see a cat sitting on a table...",
    "tokens_used": 350,
    "tokens_remaining": 99650
}
```

**Response** (409) — Token limit exceeded:
```json
{
    "session_id": "033389ac-f3ff-496a-b2e4-60e32b133fe2",
    "error": "Token limit exceeded. The conversation is too long.",
    "action": "recreate_session"
}
```

> When receiving 409, the client should create a new session and start a fresh conversation.

**Response** (404) — Session not found:
```json
{"detail": "Session 033389ac-... not found"}
```

---

## Example: Full Workflow (curl)

```bash
# 1. Create session
SESSION=$(curl -s -u admin:password -X POST http://localhost/api/v1/sessions | jq -r '.session_id')

# 2. Send text message
curl -s -u admin:password -X POST http://localhost/api/v1/chat \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION\", \"message\": \"Hello!\"}"

# 3. Send image + question
IMAGE_B64=$(base64 -w0 photo.jpg)
curl -s -u admin:password -X POST http://localhost/api/v1/chat \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION\", \"message\": \"What is in this photo?\", \"image\": \"$IMAGE_B64\"}"

# 4. Get history
curl -s -u admin:password http://localhost/api/v1/sessions/$SESSION/history

# 5. Delete session
curl -s -u admin:password -X DELETE http://localhost/api/v1/sessions/$SESSION
```
