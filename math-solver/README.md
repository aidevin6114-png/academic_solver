# Math Problem Solver - Integration Edition

A comprehensive AI-powered math problem solver integrated into the academic_solver repository with robust error handling, retry logic, and improved user experience.

## Features

- 🤖 **AI-Powered Problem Solving**: Solve math, science, and coding problems with advanced AI
- 📝 **Real-time Messaging**: Chat interface for interactive problem solving
- 📁 **Multi-Format File Support**: Upload images, PDFs, documents for analysis with validation
- 🖥️ **Screen Sharing**: Collaborative problem solving with screen sharing
- 🔍 **Web Search Integration**: AI can search the web for current information
- 💻 **Code Execution**: Write and execute code to solve problems
- 📊 **Step-by-Step Explanations**: Detailed solutions with clear steps and confidence scores
- 🛡️ **Robust Error Handling**: Comprehensive error detection and retry logic
- ⚡ **Automatic Retries**: Transient failures retry with exponential backoff
- 📋 **Error Reporting**: User-friendly error messages with actionable feedback

## Tech Stack

### Frontend
- Vue.js 3 with TypeScript
- Tailwind CSS for styling
- Pinia for state management
- Vue Router for navigation
- Axios for HTTP requests

### Backend
- Python with FastAPI
- OpenAI API for AI capabilities
- Google Vision API for OCR
- PyPDF2, python-docx for document processing
- Tesseract for local OCR
- Python logging for structured logs

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- OpenAI API key (optional, for full AI features)
- Tesseract OCR (for image text extraction)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd academic_solver
```

2. **Frontend Setup**
```bash
cd math-solver/frontend
npm install
```

3. **Backend Setup**
```bash
cd math-solver/backend
pip install -r requirements.txt
```

4. **Environment Configuration**
```bash
cd backend
cp .env.example .env
# Edit .env with your API keys and settings
# See .env.example for detailed variable documentation
```

### Running the Application

1. **Start the Backend**
```bash
cd math-solver/backend
python main.py
```
The backend will run on `http://localhost:8000`

2. **Start the Frontend (in a new terminal)**
```bash
cd math-solver/frontend
npm run dev
```
The frontend will run on `http://localhost:5173`

3. **Verify Health**
```bash
curl http://localhost:8000/health
```

## Environment Configuration

Create a `.env` file in `math-solver/backend/` using `.env.example` as a template:

```bash
# Required
OPENAI_API_KEY=sk-...
GOOGLE_CLOUD_VISION_API_KEY=...
FRONTEND_URL=http://localhost:5173

# Optional
ENVIRONMENT=development
PORT=8000
MAX_FILE_SIZE=52428800
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif,application/pdf,text/plain,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document

# Tesseract (Windows path example)
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Key Variables

- **OPENAI_API_KEY**: Required for AI problem solving. Get from https://platform.openai.com/api-keys
- **GOOGLE_CLOUD_VISION_API_KEY**: For enhanced OCR. Optional, falls back to Tesseract
- **FRONTEND_URL**: Frontend URL for CORS. Auto-expands to "*" in development mode
- **ENVIRONMENT**: Set to "development" or "production" to enable detailed logging and CORS
- **MAX_FILE_SIZE**: Maximum file size in bytes (default 50MB = 52428800)
- **TESSERACT_PATH**: Path to tesseract.exe (Windows) or tesseract (Unix)

## API Endpoints

### Core Endpoints

- `POST /api/solve/problem` - Solve a problem with optional file upload
  - Request: `multipart/form-data` with `problem`, `file`, `session_id`, `capabilities`
  - Response: `{ success, solution, steps[], code, confidence, error, errorType, sessionId, requestId }`

- `POST /api/files/upload` - Upload files for processing
  - Request: `multipart/form-data` with `file`
  - Response: `{ success, fileId, filename, error }`

- `POST /api/chat/send` - Send message to AI
  - Request: `{ role, content, file }`
  - Response: Message object with response

- `GET /api/sessions/{sessionId}` - Retrieve session history
  - Response: `{ success, messages[] }`

- `DELETE /api/sessions/{sessionId}` - Delete session
  - Response: `{ success }`

- `GET /api/health` - Health check
  - Response: `{ status, aiSolverReady, timestamp }`

### Error Response Format

All errors follow this structure:
```json
{
  "success": false,
  "error": "Human-readable error message",
  "errorType": "validation_error|file_error|ai_error|api_error|timeout_error|network_error|internal_error",
  "details": {
    "field": "additional context",
    "suggestion": "How to fix"
  },
  "retryable": true|false,
  "requestId": "uuid-for-tracing"
}
```

## Error Handling Strategy

### Error Types

| Type | Retryable | Cause | User Action |
|------|-----------|-------|-------------|
| `validation_error` | ❌ No | Invalid input (empty problem, file too large) | Fix input and retry |
| `file_error` | ❌ No | File processing failed (corrupted PDF, unsupported format) | Try different file |
| `ai_error` | ✅ Yes | AI service failure or rate limit (503, 429) | Auto-retry with backoff |
| `timeout_error` | ✅ Yes | Request took too long (>30s) | Auto-retry with backoff |
| `network_error` | ✅ Yes | Connection lost during request | Auto-retry with backoff |
| `internal_error` | ❌ No | Unexpected server error (500) | Contact support, provide requestId |

### Retry Strategy

- **Exponential backoff**: 1s → 2s → 4s → 8s with ±10% jitter
- **Max retries**: 3 attempts (configurable per endpoint)
- **Automatic retries**: Frontend auto-retries transient failures
- **User-triggered retries**: Error messages include "Retry" button for retryable errors

## File Upload Support

### Supported Formats

| Type | Formats | Processing |
|------|---------|-----------|
| Images | PNG, JPG, JPEG, GIF | OCR text extraction |
| Documents | PDF, DOCX, DOC | Text extraction |
| Text | TXT | Direct reading |

### Validation

1. **Client-side**: File extension, size (max 50MB)
2. **Server-side**: MIME type, actual size, file integrity
3. **Processing**: Format-specific extraction with error handling

### Size Limits

- Default: 50MB per file
- Configurable via `MAX_FILE_SIZE` environment variable
- Enforced client-side and server-side

## Development

### Project Structure
```
math-solver/
├── frontend/                  # Vue.js frontend
│   ├── src/
│   │   ├── services/
│   │   │   ├── apiService.ts  # API client with error handling and retries
│   │   │   └── ...
│   │   ├── views/
│   │   │   └── Solver.vue     # Main chat interface with error display
│   │   └── ...
│   └── package.json
├── backend/                   # Python backend
│   ├── services/
│   │   ├── ai_solver.py       # AI problem solving with retry logic
│   │   ├── file_processor.py  # File processing with timeouts
│   │   └── math_engine.py     # Math-specific solving
│   ├── main.py                # FastAPI app with middleware
│   ├── errors.py              # Error types and response models
│   ├── retry.py               # Retry logic and decorators
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment template
└── README.md
```

### Key Files

#### Backend Error Handling
- `backend/errors.py` (170 lines): Error hierarchy, types, response models
- `backend/retry.py` (200 lines): Retry logic, exponential backoff, decorators
- `backend/main.py` (~500 lines): API endpoints, middleware, request/response handling
- `backend/services/ai_solver.py` (~420 lines): AI integration with logging and retries
- `backend/services/file_processor.py` (~420 lines): Async file processing with validation

#### Frontend Error Handling
- `frontend/src/services/apiService.ts`: Error handling, retry logic, validation
- `frontend/src/views/Solver.vue`: Error display, retry UI, user feedback

### Testing

#### Backend Tests
```bash
cd math-solver/backend

# Test health endpoint
curl http://localhost:8000/health

# Test problem solving
curl -X POST http://localhost:8000/api/solve/problem \
  -F "problem=Solve: 2x + 3 = 7" \
  -H "X-Request-ID: test-123"

# Test file upload
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@test.pdf"

# Test error handling (missing problem)
curl -X POST http://localhost:8000/api/solve/problem \
  -F "problem=" \
  -H "Content-Type: multipart/form-data"
```

#### Frontend Tests
1. Open http://localhost:5173 in browser
2. Test error scenarios:
   - Empty problem → should show validation error
   - Large file (>50MB) → should show file size error
   - No internet → should show network error with retry button
   - Slow API → should show timeout error with retry button
3. Test retry:
   - Trigger error
   - Click retry button
   - Verify request is retried

### Common Issues

#### Issue: "OPENAI_API_KEY not set"
- **Solution**: Set `OPENAI_API_KEY` in `.env` or use mock mode for development

#### Issue: "Tesseract not found"
- **Solution**: Install Tesseract-OCR or set `GOOGLE_CLOUD_VISION_API_KEY` for cloud OCR

#### Issue: File upload fails with 422
- **Solution**: Check file size, format, and MIME type. See "File Upload Support" section

#### Issue: Backend returns 504 timeout
- **Solution**: Problem is too complex or file is large. Frontend auto-retries. Increase timeout in backend if needed.

#### Issue: CORS error in browser
- **Solution**: Set `FRONTEND_URL` in `.env` to match your frontend URL

## Deployment

### Docker Deployment

1. **Build images**
```bash
docker-compose build
```

2. **Set environment variables** (create `.env.production`)
```bash
OPENAI_API_KEY=sk-...
ENVIRONMENT=production
FRONTEND_URL=https://yourdomain.com
```

3. **Run containers**
```bash
docker-compose up -d
```

### Vercel/Netlify (Frontend)

1. Connect GitHub repository
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Set environment variable: `VITE_API_BASE_URL=https://your-api.com/api`

### Cloud Run/App Engine (Backend)

1. Create `.env` file with production variables
2. Deploy using Cloud SDK:
```bash
gcloud app deploy
```

## API Integration Guide

### Solving a Problem

**Step 1**: Send problem to AI solver
```javascript
const response = await apiService.solveProblem({
  problem: "Solve: 2x + 3 = 7",
  capabilities: {
    webSearch: true,
    codeExecution: true,
    stepByStep: true
  }
})
```

**Step 2**: Handle response
```javascript
if (response.success) {
  // Display solution, steps, code
  console.log(response.solution)
  console.log(response.steps)
  console.log(response.confidence)
} else {
  // Display error with retry button
  console.error(response.error, response.errorType)
}
```

**Step 3**: Handle errors with retry
```javascript
try {
  const response = await apiService.solveProblem(request)
} catch (error) {
  if (error.retryable) {
    // Show "Retry" button to user
  } else {
    // Show error message without retry
  }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes with clear messages
4. Ensure tests pass
5. Push to the branch
6. Open a Pull Request

## Performance Optimization

- Frontend retries transient failures automatically
- Conversation history cached in memory (backend)
- File uploads validated before sending
- Regex-based parsing for fast step extraction
- Thread pool for blocking I/O (file operations)

## Security Considerations

- ✅ No hardcoded API keys (use environment variables)
- ✅ File upload validation (size, type, content)
- ✅ CORS configured properly
- ✅ Input sanitization for problem statements
- ✅ Request ID tracking for audit logs
- ⚠️ TODO: Add authentication for production

## License

MIT License

## Support

For issues and questions:
1. Check error messages for suggestions
2. Review logs with requestId for debugging
3. Open an issue on the repository with requestId and error type