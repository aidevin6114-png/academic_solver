# Math-Solver Integration Guide

This document explains how the math-solver application has been integrated into the academic_solver repository, the improvements made, and how to use and extend it.

## Overview

The math-solver application provides an AI-powered interface for solving academic problems with comprehensive error handling, retry logic, and a user-friendly frontend. It has been integrated with significant improvements to reliability, error reporting, and user experience.

## What Was Changed

### Phase 1: Security Hardening ✅

**Removed hardcoded API keys** from docker-compose.yml and moved to environment variables.

**Files Modified:**
- `docker-compose.yml`: Changed from `OPENAI_API_KEY=sk-xxx` to `OPENAI_API_KEY=${OPENAI_API_KEY}`
- Created `.env.example` with template for all required variables
- Created `.gitignore` to prevent accidental commits of `.env`, `__pycache__`, `uploads/`, etc.

**Security Benefits:**
- API keys are never stored in version control
- Environment-specific configuration
- Safer for team development and deployment

### Phase 2: Backend Error Handling & Retry Logic ✅

**Created robust error handling infrastructure:**

**New Files:**
- `backend/errors.py` (170 lines): Error types, response models, HTTP status mappings
- `backend/retry.py` (200 lines): Retry logic with exponential backoff

**Error Hierarchy:**
```
APIError (base)
├── ValidationError (400)
├── FileError (422)
├── AIError (503)
├── TimeoutError (504)
├── RateLimitError (429)
└── APIError (500+)
```

**Retry Configuration:**
```python
DEFAULT_API_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    base_delay=1,
    backoff_multiplier=2,
    max_delay=60,
    jitter=0.1
)
```

**Modified Files:**
- `backend/main.py`: Complete rewrite (~500 lines) with error middleware, request ID tracking
- `backend/services/ai_solver.py`: Rewritten with logging, retry wrapper, conversation history
- `backend/services/file_processor.py`: Rewritten with async I/O, timeouts, validation

### Phase 3: Frontend Error Handling & UX ✅

**Improved frontend API integration and user experience:**

**Modified Files:**
- `frontend/src/services/apiService.ts`: Rewritten with error handling, retry logic, validation
- `frontend/src/views/Solver.vue`: Redesigned with error display, retry buttons, better UX

**Features Added:**
- Error banner with dismissible messages
- Retry button for retryable errors
- File validation (size, type)
- Confidence scores for solutions
- Step-by-step breakdown
- Loading states
- Session persistence with localStorage

### Phase 4: Documentation ✅

**Created comprehensive documentation:**

**Files Created/Updated:**
- `README.md` (expanded to 300+ lines): Setup, configuration, error handling guide
- `INTEGRATION_GUIDE.md` (this file): Integration details and extending the system

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Vue.js)                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Solver.vue                                            │  │
│  │  - Chat interface with error display                  │  │
│  │  - File upload with validation                        │  │
│  │  - Retry buttons for failed requests                  │  │
│  │  - Session persistence (localStorage)                 │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  apiService.ts                                         │  │
│  │  - Request/response interceptors                       │  │
│  │  - Error handling by HTTP status code                 │  │
│  │  - Automatic retry with exponential backoff           │  │
│  │  - Request validation                                 │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓ HTTP ↑
                    (with X-Request-ID header)
┌─────────────────────────────────────────────────────────────┐
│                   Backend (Python/FastAPI)                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  main.py                                               │  │
│  │  - Error middleware (catches APIError)                │  │
│  │  - Request ID middleware (generates UUID)             │  │
│  │  - CORS configuration                                 │  │
│  │  - Health check endpoint                              │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  services/ai_solver.py                                 │  │
│  │  - Structured logging                                 │  │
│  │  - Retry wrapper (@retry_on_exception)               │  │
│  │  - Conversation history (in-memory per session)       │  │
│  │  - Regex-based step/code extraction                  │  │
│  │  - Mock fallback when API unavailable                │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  services/file_processor.py                            │  │
│  │  - ThreadPoolExecutor for async I/O                   │  │
│  │  - asyncio.wait_for() timeout handling                │  │
│  │  - File validation (size, type, integrity)            │  │
│  │  - Graceful handling of missing dependencies          │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  errors.py & retry.py                                  │  │
│  │  - Error type definitions                             │  │
│  │  - Response model schemas                             │  │
│  │  - Retry logic with exponential backoff               │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

### User Submits Problem

```
User Input
    ↓
Frontend Validation (size, type)
    ↓ (valid)
apiService.solveProblem()
    ↓
Request Interceptor (add X-Request-ID)
    ↓
Backend /api/solve/problem
    ↓
Input Validation (400) → Frontend: "Invalid problem"
    ↓ (valid)
File Processing (if any)
    ↓
File Validation (422) → Frontend: "File too large" (retryable)
    ↓ (valid)
AI Solver
    ↓
OpenAI Rate Limit (429) → Auto-retry with backoff
    ↓
OpenAI API Timeout (504) → Auto-retry with backoff
    ↓
OpenAI Error (503) → Auto-retry, then fallback to mock
    ↓ (success)
Response Validation (check required fields)
    ↓
Return to Frontend
    ↓
Response Interceptor (handle errors by status)
    ↓
Display Solution OR Display Error + Retry Button
```

## Configuration

### Environment Variables

All variables are optional with sensible defaults. Set them in `.env` file:

```bash
# API Keys (required for full features)
OPENAI_API_KEY=sk-your-key-here
GOOGLE_CLOUD_VISION_API_KEY=your-key-here

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:5173

# Server
ENVIRONMENT=development  # or production
PORT=8000

# File Upload
MAX_FILE_SIZE=52428800  # 50MB in bytes
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif,application/pdf,text/plain,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document

# OCR (for Windows)
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Development vs Production

**Development Mode:**
- `ENVIRONMENT=development`
- Detailed logging enabled
- CORS allows any origin (http://localhost:*)
- Mock AI responses if API key not set

**Production Mode:**
- `ENVIRONMENT=production`
- Minimal logging (errors only)
- CORS restricted to FRONTEND_URL only
- Errors require valid API key

## Testing the Integration

### 1. Health Check
```bash
curl http://localhost:8000/health
# Response: { "status": "ok", "aiSolverReady": true, "timestamp": "2024-01-01T00:00:00Z" }
```

### 2. Solve a Simple Problem
```bash
curl -X POST http://localhost:8000/api/solve/problem \
  -F "problem=Solve: 2x + 3 = 7" \
  -F "capabilities={\"webSearch\":true,\"codeExecution\":false,\"stepByStep\":true}"
```

### 3. Test Error Handling
```bash
# Validation error (empty problem)
curl -X POST http://localhost:8000/api/solve/problem \
  -F "problem=" \
  -F "capabilities={\"webSearch\":true,\"codeExecution\":false,\"stepByStep\":true}"

# Response: { "success": false, "error": "Problem statement cannot be empty", "errorType": "validation_error", "retryable": false }
```

### 4. Test File Upload
```bash
# Success
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@test.pdf"

# File too large (>50MB)
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@huge-file.pdf"
# Response: { "success": false, "error": "File exceeds maximum size", "errorType": "file_error", "retryable": false }
```

### 5. Frontend Testing
1. Open http://localhost:5173
2. Try submitting an empty problem → validation error
3. Try uploading a >50MB file → file error
4. With no internet → network error with retry button
5. Slow API → timeout error with retry button

## Extending the System

### Adding a New Error Type

1. Add to `ErrorType` enum in `errors.py`:
```python
class ErrorType(str, Enum):
    CUSTOM_ERROR = "custom_error"
```

2. Create error class:
```python
class CustomError(APIError):
    def __init__(self, details: dict | None = None):
        super().__init__(
            message="Custom error message",
            error_type=ErrorType.CUSTOM_ERROR,
            status_code=400,
            retryable=False,
            details=details
        )
```

3. Use in code:
```python
raise CustomError(details={"field": "value"})
```

4. Frontend automatically handles it:
```javascript
if (error.type === ErrorType.CUSTOM_ERROR) {
  // Handle custom error
}
```

### Adding a New API Endpoint

1. Create handler in `main.py`:
```python
@app.post("/api/new-endpoint")
async def new_endpoint(request: NewRequest) -> NewResponse:
    request_id = request.state.request_id
    logger.info(f"Processing new endpoint request: {request_id}")
    
    try:
        # Your logic here
        return NewResponse(success=True, data=result)
    except APIError:
        raise  # Error middleware will handle
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise APIError("An error occurred", retryable=False)
```

2. Add to frontend service:
```typescript
async newEndpoint(request: NewRequest): Promise<NewResponse> {
  return retryWithBackoff(async () => {
    const response = await api.post('/new-endpoint', request)
    return validateResponse<NewResponse>(response.data, ['success'])
  })
}
```

### Improving AI Problem Solving

The AI solver uses conversation history to maintain context:

```python
# In ai_solver.py, solve_problem() method:
if session_id not in self.sessions:
    self.sessions[session_id] = []

# Add user message to history
self.sessions[session_id].append({
    "role": "user",
    "content": problem
})

# Pass last 10 messages to OpenAI for context
messages = self.sessions[session_id][-10:]

# Get response
response = await self._call_openai_with_retry(messages)

# Add to history
self.sessions[session_id].append({
    "role": "assistant",
    "content": response
})
```

To add more context or improve extraction:

1. Enhance system prompt in `_call_openai()`:
```python
system_prompt = """You are an expert academic problem solver...
IMPORTANT: Always provide solutions in this format:
Steps:
1. ...
2. ...

Code (if applicable):
```python
...
```
"""
```

2. Improve extraction regex in `_extract_steps()`:
```python
# Current pattern
pattern = r'(?:^|\n)\s*(?:Step\s+\d+|[0-9]+\.)\s*(?::)?\s*(.+?)(?=(?:Step\s+\d+|[0-9]+\.|$))'

# Customize for your domain
pattern = r'(?:^|\n)\s*(?:Step|Action)\s+\d+[.:]?\s+(.+?)(?=(?:Step|Action)\s+\d+|$)'
```

### Adding Persistent Storage

The current system uses in-memory sessions (lost on restart). To add persistent storage:

1. Create `backend/session_storage.py`:
```python
import sqlite3
import json

class SessionStorage:
    def __init__(self, db_path="sessions.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                messages JSON,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def save_session(self, session_id: str, messages: list):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO sessions (id, messages, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (session_id, json.dumps(messages)))
        conn.commit()
        conn.close()
    
    def load_session(self, session_id: str) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT messages FROM sessions WHERE id = ?",
            (session_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return json.loads(row[0]) if row else []
```

2. Update `AISolver` to use storage:
```python
from session_storage import SessionStorage

class AISolver:
    def __init__(self):
        self.storage = SessionStorage()
    
    def solve_problem(self, problem: str, session_id: str) -> dict:
        # Load session
        messages = self.storage.load_session(session_id)
        
        # Use messages as before
        messages.append({"role": "user", "content": problem})
        response = await self._call_openai_with_retry(messages)
        messages.append({"role": "assistant", "content": response})
        
        # Save session
        self.storage.save_session(session_id, messages)
        
        return parse_response(response)
```

## Troubleshooting

### Issue: "OPENAI_API_KEY not found"

**Solution**: Mock mode is active. Set real API key in `.env`:
```bash
OPENAI_API_KEY=sk-your-key-here
```

### Issue: "Tesseract not found"

**Solution**: Install Tesseract or use Google Vision API:
```bash
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Update TESSERACT_PATH in .env

# macOS: brew install tesseract
# Linux: apt-get install tesseract-ocr
```

### Issue: Slow responses (>30s timeout)

**Solution**: Increase timeout or optimize:
1. Increase `API_TIMEOUT` in `frontend/src/services/apiService.ts` (currently 30000ms)
2. Reduce problem complexity
3. Disable unnecessary capabilities (webSearch, codeExecution)

### Issue: "File validation failed"

**Solution**: Check:
1. File size < 50MB (configurable via MAX_FILE_SIZE)
2. File type in ALLOWED_FILE_TYPES (default: images, PDF, text, Word docs)
3. File is not corrupted

### Issue: High memory usage

**Solution**: Clear old sessions:
1. Frontend: User clicks "Clear Conversation"
2. Backend: Add cleanup task
```python
# In main.py, add periodic cleanup
import asyncio
from datetime import datetime, timedelta

async def cleanup_old_sessions():
    while True:
        await asyncio.sleep(3600)  # Every hour
        cutoff = datetime.now() - timedelta(hours=24)
        # Remove sessions older than 24 hours
```

## Performance Tips

1. **Reduce token usage**: Limit conversation history to last 5 messages
2. **Cache results**: Store responses for common problems
3. **Batch requests**: Send multiple problems in one request if possible
4. **Optimize extraction**: Use faster regex patterns or pre-compiled patterns
5. **Monitor tokens**: Log token usage to identify expensive operations

## Security Checklist

- [ ] API keys stored in `.env`, not in code
- [ ] `.env` added to `.gitignore`
- [ ] `.gitignore` includes `__pycache__`, `uploads/`, `node_modules/`
- [ ] CORS configured for your domain only (production)
- [ ] File uploads validated (size, type, content)
- [ ] Sensitive logs don't include API keys or user data
- [ ] Request ID included for audit trail
- [ ] Production mode enabled with ENVIRONMENT=production

## Next Steps

1. **Add authentication**: Use JWT or OAuth for user sessions
2. **Implement rate limiting**: Prevent abuse via request quota
3. **Add caching**: Store frequent problems/solutions
4. **Improve AI**: Fine-tune for specific domains
5. **Analytics**: Track success rates and performance
6. **Testing**: Add unit and integration tests
7. **Monitoring**: Add alerts for errors and timeouts

## Support

For issues:
1. Check error messages and `requestId`
2. Review logs with `requestId`
3. Check environment variables
4. Test individual components (health check, file upload, etc.)
5. Open an issue with error type, requestId, and reproduction steps
