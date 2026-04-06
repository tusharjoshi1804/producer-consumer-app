# Producer-Consumer App

Two Django microservices communicating over HTTP in Docker containers.

- **Producer** (port 8000): Receives delete requests from clients and forwards them to the Consumer.
- **Consumer** (port 8001): Owns the resources, validates auth, and processes deletes.

---

## Architecture

```
Client
  │
  ▼
Producer (POST /send-delete/<id>/)   port 8000
  │  validates ID, adds auth token
  ▼
Consumer (DELETE /resource/<id>/)    port 8001
  │  checks auth, deletes resource
  ▼
Response forwarded back to Client
```

---

## Quick Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/)

### Run the services

```bash
git clone <your-repo-url>
cd producer_consumer_app
docker-compose up --build
```

Both services will start:
- Producer → http://localhost:8000
- Consumer → http://localhost:8001

---

## API Reference

### Producer

#### `POST /send-delete/<id>/`
Sends a delete request to the Consumer for the given resource ID.

```bash
curl -X POST http://localhost:8000/send-delete/42/
```

**Responses:**

| Status | Meaning |
|--------|---------|
| 200 | Resource deleted successfully |
| 400 | Invalid resource ID format |
| 401 | Auth token rejected by Consumer |
| 404 | Resource not found / already deleted |
| 503 | Consumer service is unreachable |
| 504 | Request to Consumer timed out |
| 502 | Consumer returned unexpected error |

---

### Consumer

#### `DELETE /resource/<id>/`
Deletes a resource by ID. Requires `Authorization: Bearer mysecrettoken` header.

```bash
curl -X DELETE http://localhost:8001/resource/42/ \
  -H "Authorization: Bearer mysecrettoken"
```

#### `GET /resources/`
Lists all currently available resources (dev/debug helper).

```bash
curl http://localhost:8001/resources/ \
  -H "Authorization: Bearer mysecrettoken"
```

---

## Edge Cases Handled

| # | Scenario | HTTP Status |
|---|----------|-------------|
| 1 | Resource not found | 404 |
| 2 | Consumer service is down | 503 |
| 3 | Invalid ID format (non-integer) | 400 |
| 4 | Resource already deleted (idempotent) | 404 |
| 5 | Missing or wrong auth token | 401 |
| 6 | Consumer doesn't respond in time (5s timeout) | 504 |
| 7 | Consumer returns 5xx error | 502 |

---

## Pre-loaded Resources

The Consumer starts with these resources in memory:

| ID | Name |
|----|------|
| 1 | Resource Alpha |
| 2 | Resource Beta |
| 3 | Resource Gamma |
| 42 | Resource Delta |
| 100 | Resource Epsilon |

---

## Example Requests

```bash
# Success — delete resource 42
curl -X POST http://localhost:8000/send-delete/42/

# 404 — resource doesn't exist
curl -X POST http://localhost:8000/send-delete/999/

# 400 — invalid ID
curl -X POST http://localhost:8000/send-delete/abc/

# 404 — already deleted (idempotent)
curl -X POST http://localhost:8000/send-delete/42/
curl -X POST http://localhost:8000/send-delete/42/  # returns 404
```

---

## Configuration

Environment variables (set in `docker-compose.yml`):

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `CONSUMER_URL` | Producer | `http://consumer:8001` | Base URL of Consumer service |
| `SECRET_TOKEN` | Both | `mysecrettoken` | Shared auth token |

---

## Tech Stack

- **Language:** Python 3.11
- **Framework:** Django 4.2 + Django REST Framework 3.14
- **Communication:** HTTP via `requests` library
- **Auth:** Shared Bearer token in `Authorization` header
- **Containerization:** Docker + Docker Compose

---

## Project Structure

```
producer_consumer_app/
├── docker-compose.yml
├── producer_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── producer_service/
│   │   ├── settings.py
│   │   └── urls.py
│   └── producer/
│       ├── views.py       # send_delete + error handling
│       └── urls.py
└── consumer_service/
    ├── Dockerfile
    ├── requirements.txt
    ├── manage.py
    ├── consumer_service/
    │   ├── settings.py
    │   └── urls.py
    └── consumer/
        ├── models.py      # in-memory resource store
        ├── views.py       # delete_resource + auth check
        └── urls.py
```
