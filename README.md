
# AI Assistant Task Processor

> Asynchronous API service for processing LLM requests using Claude AI, FastAPI, Celery, and Redis

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)

---

## 📋 Project Overview

This project implements a production-grade asynchronous task processing system that accepts user prompts, processes them through Claude AI in the background using Celery workers, and provides real-time status updates through REST API endpoints.

### Key Achievement
✨ **Immediate API response (~50ms) while Claude AI processes in background (~5-30s)** - demonstrating true asynchronous architecture

---

## 🎯 Problem Statement

**Challenge:** LLM API calls typically take 5-30 seconds, blocking the API server and creating poor user experience.

**Solution:** Implemented distributed task queue architecture where:
1. User submits request → Receives task ID immediately
2. Celery worker processes LLM request asynchronously
3. User polls status endpoint → Retrieves results when ready

**Result:** Non-blocking API that can handle multiple concurrent requests efficiently.

---

## 🏗️ Architecture
```
┌─────────┐
│  User   │
└────┬────┘
     │ POST /submit (prompt)
     ▼
┌─────────────┐
│   FastAPI   │ ← Returns task_id immediately (~50ms)
│   Server    │
└──────┬──────┘
       │ Publishes task to queue
       ▼
┌─────────────┐
│    Redis    │ ← Message Broker + Result Backend
│  (In-Memory)│
└──────┬──────┘
       │ Worker polls for tasks
       ▼
┌─────────────┐
│   Celery    │ ← Processes in background
│   Worker    │
└──────┬──────┘
       │ API Call
       ▼
┌─────────────┐
│  Claude AI  │ ← Generates response (~5-30s)
│  (Anthropic)│
└──────┬──────┘
       │ Result stored in Redis
       ▼
┌─────────────┐
│    User     │ ← GET /status/{task_id} retrieves result
└─────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop (or GitHub Codespaces)
- Anthropic API Key

### Using GitHub Codespaces (Recommended)

1. **Open in Codespaces**
   - Navigate to this repository on GitHub
   - Click `Code` → `Codespaces` → `Create codespace on main`

2. **Configure API Key**
```bash
   # Create .env file
   cp .env.example .env
   # Add your Anthropic API key to .env
```

3. **Launch Services**
```bash
   docker-compose up --build
```

4. **Access API**
   - Codespaces will provide a URL (e.g., `https://xxx-8000.app.github.dev`)
   - Navigate to `/docs` for interactive API documentation

### Local Setup
```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/ai-assistant-task-processor.git
cd ai-assistant-task-processor

# Configure environment
cp .env.example .env
# Edit .env with your API key

# Start services
docker-compose up --build

# Access API
open http://localhost:8000/docs
```

---

## 📡 API Endpoints

### Core Endpoints

#### 1. Submit Task
**Endpoint:** `POST /submit`

**Request:**
```json
{
  "prompt": "Explain asynchronous processing in simple terms"
}
```

**Response:**
```json
{
  "task_id": "abc-123-def-456",
  "status": "PENDING",
  "message": "Task submitted successfully"
}
```

#### 2. Check Status
**Endpoint:** `GET /status/{task_id}`

**Response (Pending):**
```json
{
  "task_id": "abc-123-def-456",
  "status": "PENDING",
  "result": null
}
```

**Response (Success):**
```json
{
  "task_id": "abc-123-def-456",
  "status": "SUCCESS",
  "result": {
    "response": "Asynchronous processing allows programs...",
    "model": "claude-sonnet-4-5-20250929",
    "prompt": "Explain asynchronous processing...",
    "prompt_length": 42,
    "response_length": 1456,
    "timestamp": 1730195847.123,
    "task_id": "abc-123-def-456"
  }
}
```

#### 3. Health Check
**Endpoint:** `GET /health`
```json
{
  "status": "healthy",
  "service": "AI Assistant Task Processor"
}
```

### Bonus Endpoints

#### 4. Cancel Task
**Endpoint:** `DELETE /cancel/{task_id}`

Terminates a running or pending task.

#### 5. List Recent Tasks
**Endpoint:** `GET /tasks/recent`

Returns active, scheduled, and reserved tasks across all workers.

---

## 🧪 Testing Guide

### Using Interactive Documentation

1. **Navigate to `/docs`**
2. **Expand `POST /submit`** → Click "Try it out"
3. **Enter prompt** → Click "Execute"
4. **Copy `task_id`** from response
5. **Expand `GET /status/{task_id}`** → Paste task_id
6. **Click "Execute"** → Check status
7. **Wait 10-15 seconds** if status is PENDING
8. **Click "Execute" again** → View SUCCESS with Claude's response

### Using cURL
```bash
# Submit task
curl -X POST "http://localhost:8000/submit" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is Docker?"}'

# Copy task_id from response, then:
curl "http://localhost:8000/status/TASK_ID_HERE"
```

### Expected Flow
```
1. Submit → Status: PENDING (instant response)
2. Wait 5-10s → Status: PROCESSING (worker picked up task)
3. Wait 5-10s → Status: SUCCESS (Claude responded)
4. Result contains full LLM response with metadata
```

---

## 🎯 Key Features Implemented

### Core Requirements ✅

- [x] **FastAPI** for REST API endpoints
- [x] **Environment-based configuration** (API keys never hardcoded)
- [x] **Celery** with Redis for asynchronous task processing
- [x] **Immediate response** with task ID
- [x] **Status endpoint** to check task completion
- [x] **LLM API integration** in Celery worker
- [x] **Post-processing** (whitespace trimming, metadata addition)
- [x] **Comprehensive documentation**

### Bonus Features ✅

- [x] **Docker Compose** for multi-container orchestration
- [x] **Task cancellation** endpoint
- [x] **List recent tasks** endpoint
- [x] **Auto-generated API docs** (Swagger UI + ReDoc)
- [x] **Health check** endpoint
- [x] **Error handling** with proper status codes
- [x] **Logging** throughout application

---

## 🛠️ Tech Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **API Framework** | FastAPI | 0.104.1 | REST API server with auto-docs |
| **Task Queue** | Celery | 5.3.4 | Distributed background processing |
| **Message Broker** | Redis | 7-alpine | Task queue and result storage |
| **LLM Provider** | Anthropic Claude | API | Text generation |
| **Validation** | Pydantic | 2.5.0 | Request/response validation |
| **Web Server** | Uvicorn | 0.24.0 | ASGI server |
| **Containerization** | Docker Compose | 3.8 | Service orchestration |
| **HTTP Client** | httpx | 0.27.0 | Async HTTP requests |

---

## 📁 Project Structure
```
ai-assistant-task-processor/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Settings management (Pydantic)
│   ├── tasks.py             # Celery tasks (LLM processing)
│   └── main.py              # FastAPI application (endpoints)
├── .env                     # Environment variables (not committed)
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Multi-service orchestration
└── README.md                # This file
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Claude API authentication key | `sk-ant-api03-...` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | Celery message broker | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Result storage backend | `redis://redis:6379/0` |

**Security Note:** Never commit `.env` file. Use `.env.example` as template.

---

## 🤔 Design Decisions

### Why Celery?
- **Distributed architecture:** Workers can run on separate machines
- **Persistence:** Tasks survive API server restarts
- **Monitoring:** Built-in tools (Flower) for task inspection
- **Scalability:** Add more workers to handle increased load

### Why Redis?
- **Dual purpose:** Acts as both message broker and result backend
- **Speed:** In-memory storage for low-latency task retrieval
- **Simplicity:** Single service for development
- **Production-ready:** Scales to millions of messages/second

### Why FastAPI?
- **Performance:** Async support matches Node.js speed
- **Developer experience:** Auto-generated documentation
- **Type safety:** Pydantic validation prevents runtime errors
- **Modern:** Built on Python 3.6+ type hints

### Why Docker?
- **Consistency:** "Works on my machine" → "Works everywhere"
- **Isolation:** Services don't interfere with each other
- **Scalability:** Easy horizontal scaling with `docker-compose scale`
- **Production parity:** Development environment matches deployment

---

## ⚠️ Assumptions & Limitations

### Assumptions
- **Single-tenant:** No multi-user authentication required
- **Moderate load:** <100 concurrent tasks (single worker)
- **Task completion:** All tasks complete within 5 minutes
- **Result retention:** Redis default TTL (24 hours)

### Current Limitations
- **No authentication:** Public API (implement JWT for production)
- **No rate limiting:** Vulnerable to abuse (add per-IP limits)
- **No persistent storage:** Task history lost on Redis restart
- **Single Redis instance:** No high availability
- **No retry logic:** Failed tasks don't automatically retry

### Known Issues
- Very long prompts (>10,000 chars) may timeout
- Task cancellation may not work for in-progress Claude API calls
- No webhook notifications when tasks complete

---

## 🚀 Future Enhancements

### High Priority
- [ ] JWT authentication with user management
- [ ] Rate limiting (per-user quotas)
- [ ] PostgreSQL for persistent task history
- [ ] Automatic retry with exponential backoff
- [ ] Prometheus metrics + Grafana dashboards

### Medium Priority
- [ ] Webhook notifications on task completion
- [ ] Task priority queues (urgent vs. normal)
- [ ] Result caching for duplicate prompts
- [ ] Streaming responses (Server-Sent Events)
- [ ] Multi-model support (OpenAI, Cohere, etc.)

### Low Priority
- [ ] Admin dashboard for task management
- [ ] Scheduled tasks (run at specific time)
- [ ] Task dependencies (chain multiple tasks)
- [ ] Batch processing (submit multiple prompts)
- [ ] A/B testing framework

---

## 📊 Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **API Response Time** | ~50ms | Task submission (no LLM call) |
| **LLM Processing Time** | 5-30s | Depends on prompt complexity |
| **Status Check Time** | ~10ms | Redis lookup |
| **Throughput** | 1 task/worker | Parallel processing per worker |
| **Max Concurrent Tasks** | Workers × Concurrency | Default: 2 workers × 2 = 4 |

### Scaling Strategy
```bash
# Scale to 5 workers
docker-compose up --scale worker=5

# Expected throughput: 10 concurrent tasks
```

---

## 🐛 Troubleshooting

### Issue: "Connection refused" on startup
**Cause:** Services starting in wrong order  
**Solution:** Wait 30 seconds for Redis healthcheck to pass

### Issue: Task stays PENDING forever
**Cause:** Celery worker not running or crashed  
**Solution:** Check logs with `docker-compose logs worker`

### Issue: "Invalid API key" error
**Cause:** Wrong or missing Anthropic API key  
**Solution:** Verify `.env` file has correct key format: `sk-ant-api03-...`

### Issue: Port 8000 already in use
**Cause:** Another service using the port  
**Solution:** Change port in `docker-compose.yml` or stop conflicting service

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f worker
docker-compose logs -f api
```

---

## 🧪 Testing Checklist

- [x] All containers start successfully
- [x] `/docs` endpoint accessible
- [x] Can submit task and receive task_id
- [x] Task status transitions: PENDING → PROCESSING → SUCCESS
- [x] Claude AI response received in result
- [x] Error handling (invalid API key scenario tested)
- [x] Cancel endpoint terminates tasks
- [x] List endpoint shows active tasks
- [x] Health check returns 200 OK

---

## 📚 Development Notes

### Local Development Without Docker
```bash
# Install dependencies
pip install -r requirements.txt

# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery worker
celery -A app.tasks worker --loglevel=info

# Terminal 3: Start FastAPI
uvicorn app.main:app --reload
```

### Code Quality
- **Type hints:** Used throughout for IDE support
- **Docstrings:** All functions documented
- **Logging:** Comprehensive logging at INFO level
- **Error handling:** Try-except blocks with proper exceptions
- **Validation:** Pydantic models for all inputs/outputs

---

## 🎓 Learning Outcomes

This project demonstrates understanding of:

✅ **Async Architecture:** Non-blocking I/O with background processing  
✅ **Distributed Systems:** Message queues and worker pools  
✅ **API Design:** RESTful principles with proper status codes  
✅ **DevOps:** Containerization and service orchestration  
✅ **LLM Integration:** API authentication and response handling  
✅ **Error Handling:** Graceful degradation and informative errors  
✅ **Documentation:** Self-documenting code and comprehensive README  

---

## 🌟 Production Considerations

### Before Deploying to Production

1. **Security**
   - [ ] Add JWT authentication
   - [ ] Implement HTTPS only
   - [ ] Use secrets management (AWS Secrets Manager)
   - [ ] Add CORS whitelist
   - [ ] Rate limiting per user/IP

2. **Reliability**
   - [ ] Redis cluster (HA setup)
   - [ ] Task retry logic
   - [ ] Circuit breakers for external APIs
   - [ ] Database for persistent storage
   - [ ] Backup and recovery plan

3. **Monitoring**
   - [ ] Prometheus + Grafana
   - [ ] Sentry for error tracking
   - [ ] APM tool (DataDog, New Relic)
   - [ ] Log aggregation (ELK stack)
   - [ ] Uptime monitoring

4. **Performance**
   - [ ] Load balancer for API servers
   - [ ] Auto-scaling workers based on queue length
   - [ ] CDN for static assets
   - [ ] Database connection pooling
   - [ ] Response caching

--
---

## 🙏 Acknowledgments

- **Anthropic** for Claude AI API
- **FastAPI** team for excellent framework
- **Celery** community for robust task queue
- **Docker** for containerization platform
