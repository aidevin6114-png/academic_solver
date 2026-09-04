import os
import logging
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from services.ai_solver import AISolver
from services.file_processor import FileProcessor
from services.math_engine import MathEngine
from errors import (
    APIError, ValidationError, FileError, AIError, APIServiceError,
    TimeoutError as TimeoutErrorClass, ErrorResponse, create_error_response
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
ai_solver = AISolver()
file_processor = FileProcessor()
math_engine = MathEngine()

# Create directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("sessions", exist_ok=True)

# Get configuration from environment
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "png,jpg,jpeg,gif,bmp,pdf,docx,doc,txt").split(",")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# In-memory session storage (replace with database in production)
sessions: Dict[str, list] = {}


# Data models
class ChatMessage(BaseModel):
    role: str
    content: str
    file: Optional[dict] = None


class SolveRequest(BaseModel):
    problem: str = Field(..., min_length=1, max_length=5000, description="Problem statement")
    capabilities: Dict[str, bool] = Field(default={}, description="Enabled capabilities")
    file_id: Optional[str] = None


class SolveResponse(BaseModel):
    success: bool
    solution: Optional[str] = None
    steps: Optional[list[str]] = None
    code: Optional[str] = None
    confidence: Optional[float] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None


class FileUploadResponse(BaseModel):
    success: bool
    file_id: Optional[str] = None
    filename: Optional[str] = None
    file_type: Optional[str] = None
    error: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting Math Problem Solver API in {ENVIRONMENT} mode")
    logger.info(f"Frontend URL: {FRONTEND_URL}")
    yield
    # Shutdown
    logger.info("Shutting down Math Problem Solver API")


# Create FastAPI app
app = FastAPI(
    title="Math Problem Solver API",
    description="AI-powered math problem solver with file processing and collaborative features",
    version="1.0.0",
    lifespan=lifespan
)


# CORS middleware with environment-based configuration
cors_origins = [FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"]
if ENVIRONMENT == "development":
    cors_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Error handler for APIError exceptions
@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    request_id = getattr(request.state, "request_id", None)
    error_response = create_error_response(exc, request_id)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )


# Middleware to add request ID
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# API Routes
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Math Problem Solver API",
        "version": "1.0.0",
        "status": "healthy",
        "environment": ENVIRONMENT
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ai_solver_ready": ai_solver.openai_api_key is not None
    }


@app.post("/api/chat/send")
async def send_message(message: ChatMessage, request: Request):
    """Send a message to the AI solver"""
    request_id = request.state.request_id
    session_id = str(uuid.uuid4())
    
    logger.info(f"Chat message received (request_id={request_id}, session_id={session_id})")
    
    try:
        if not message.content or not message.content.strip():
            raise ValidationError("Message content cannot be empty")
        
        # Store message in session
        if session_id not in sessions:
            sessions[session_id] = []
        
        sessions[session_id].append({
            "role": message.role,
            "content": message.content,
            "timestamp": datetime.now().isoformat(),
            "file": message.file
        })
        
        # For now, return mock response (integrate with AI solver as needed)
        return {
            "success": True,
            "message_id": str(uuid.uuid4()),
            "session_id": session_id,
            "request_id": request_id,
            "response": "Message received and stored in session"
        }
        
    except ValidationError as e:
        logger.error(f"Validation error in send_message: {str(e)}", extra={"request_id": request_id})
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in send_message (request_id={request_id})")
        raise APIError(
            f"Failed to process message: {str(e)}",
            status_code=500
        )


@app.post("/api/files/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...), request: Request = None):
    """Upload a file for processing"""
    request_id = request.state.request_id if request else str(uuid.uuid4())
    
    logger.info(f"File upload started (request_id={request_id}, filename={file.filename})")
    
    try:
        if not file.filename:
            raise ValidationError("Filename is required")
        
        # Validate file extension
        file_extension = file.filename.split(".")[-1].lower() if "." in file.filename else ""
        if file_extension not in ALLOWED_FILE_TYPES:
            raise ValidationError(
                f"File type .{file_extension} not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}"
            )
        
        # Read and validate file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise FileError(
                f"File size {len(content)} bytes exceeds maximum {MAX_FILE_SIZE} bytes",
                details={"max_size": MAX_FILE_SIZE, "actual_size": len(content)}
            )
        
        # Save file
        file_id = str(uuid.uuid4())
        file_path = f"uploads/{file_id}.{file_extension}"
        
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        logger.info(f"File uploaded successfully (request_id={request_id}, file_id={file_id})")
        
        return FileUploadResponse(
            success=True,
            file_id=file_id,
            filename=file.filename,
            file_type=file_extension
        )
        
    except (ValidationError, FileError) as e:
        logger.error(f"Expected error in file upload: {str(e)}", extra={"request_id": request_id})
        return FileUploadResponse(
            success=False,
            error=e.message if hasattr(e, 'message') else str(e)
        )
    except Exception as e:
        logger.exception(f"Unexpected error in file upload (request_id={request_id})")
        return FileUploadResponse(
            success=False,
            error=f"File upload failed: {str(e)}"
        )


@app.post("/api/solve/problem", response_model=SolveResponse)
async def solve_problem(
    problem: str = Form(...),
    capabilities: str = Form(default="{}"),
    session_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    request: Request = None
):
    """Solve a math problem with AI"""
    request_id = request.state.request_id if request else str(uuid.uuid4())
    session_id = session_id or str(uuid.uuid4())
    
    logger.info(f"Solve problem requested (request_id={request_id}, session_id={session_id})")
    
    try:
        # Validate and parse capabilities
        try:
            capabilities_dict = json.loads(capabilities)
        except json.JSONDecodeError:
            raise ValidationError("Invalid capabilities JSON format")
        
        if not isinstance(capabilities_dict, dict):
            raise ValidationError("Capabilities must be a JSON object")
        
        # Process file if provided
        file_data = None
        extracted_text = None
        
        if file:
            logger.info(f"Processing file: {file.filename} (request_id={request_id})")
            
            file_id = str(uuid.uuid4())
            file_extension = file.filename.split(".")[-1].lower() if "." in file.filename else ""
            file_path = f"uploads/{file_id}.{file_extension}"
            
            # Save file
            content = await file.read()
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            
            # Process file with OCR/extraction
            try:
                process_result = await file_processor.process_file(file_path, file_extension)
                
                if process_result.get("success"):
                    extracted_text = process_result.get("text", "")
                    logger.info(f"File processed successfully (request_id={request_id}, text_length={len(extracted_text)})")
                else:
                    logger.warning(f"File processing had issues: {process_result.get('error')}")
                
                file_data = {
                    "file_id": file_id,
                    "filename": file.filename,
                    "file_type": file_extension,
                    "text": extracted_text
                }
            
            except Exception as e:
                logger.error(f"File processing error: {str(e)}", extra={"request_id": request_id})
                raise FileError(
                    f"Failed to process file: {str(e)}",
                    details={"filename": file.filename}
                )
        
        # Try math engine first for mathematical problems
        try:
            math_result = math_engine.solve_equation(problem)
            if math_result.get("success"):
                logger.info(f"Problem solved by math engine (request_id={request_id})")
                return SolveResponse(
                    success=True,
                    solution=f"Mathematical solution: {', '.join(math_result.get('solutions', []))}",
                    steps=math_result.get("steps", []),
                    code=None,
                    confidence=0.95,
                    session_id=session_id,
                    request_id=request_id
                )
        except Exception as e:
            logger.debug(f"Math engine couldn't solve, falling back to AI (request_id={request_id})")
        
        # Fall back to AI solver
        ai_result = await ai_solver.solve_problem(
            problem=problem,
            capabilities=capabilities_dict,
            file_data=file_data,
            session_id=session_id,
            request_id=request_id
        )
        
        # Store in session history
        if session_id not in sessions:
            sessions[session_id] = []
        
        sessions[session_id].append({
            "role": "user",
            "content": problem,
            "file": file_data,
            "timestamp": datetime.now().isoformat()
        })
        sessions[session_id].append({
            "role": "assistant",
            "content": ai_result.get("solution"),
            "timestamp": datetime.now().isoformat()
        })
        
        return SolveResponse(
            success=ai_result.get("error") is None,
            solution=ai_result.get("solution"),
            steps=ai_result.get("steps"),
            code=ai_result.get("code"),
            confidence=ai_result.get("confidence", 0.7),
            error=ai_result.get("error"),
            error_type=ai_result.get("error_type"),
            session_id=session_id,
            request_id=request_id
        )
        
    except (ValidationError, FileError) as e:
        logger.error(f"Expected error in solve_problem: {str(e)}", extra={"request_id": request_id})
        return SolveResponse(
            success=False,
            error=e.message if hasattr(e, 'message') else str(e),
            error_type=e.error_type.value if hasattr(e, 'error_type') else "unknown",
            session_id=session_id,
            request_id=request_id
        )
    except Exception as e:
        logger.exception(f"Unexpected error in solve_problem (request_id={request_id})")
        return SolveResponse(
            success=False,
            error=f"Problem solving failed: {str(e)}",
            error_type="internal_error",
            session_id=session_id,
            request_id=request_id
        )


@app.post("/api/screenshare/create")
async def create_screen_share(request: Request = None):
    """Create a screen sharing session"""
    request_id = request.state.request_id if request else str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    
    logger.info(f"Screen share session created (request_id={request_id}, session_id={session_id})")
    
    # Mock Jitsi integration
    jitsi_domain = os.getenv("JITSI_DOMAIN", "meet.jit.si")
    jitsi_url = f"https://{jitsi_domain}/math-solver-{session_id}"
    
    return {
        "success": True,
        "session_id": session_id,
        "url": jitsi_url,
        "status": "created",
        "request_id": request_id
    }


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str, request: Request = None):
    """Get session history"""
    request_id = request.state.request_id if request else str(uuid.uuid4())
    
    if session_id not in sessions:
        logger.warning(f"Session not found (request_id={request_id}, session_id={session_id})")
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    logger.info(f"Session retrieved (request_id={request_id}, session_id={session_id}, messages={len(sessions[session_id])})")
    
    return {
        "success": True,
        "session_id": session_id,
        "messages": sessions[session_id],
        "request_id": request_id
    }


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, request: Request = None):
    """Delete session history"""
    request_id = request.state.request_id if request else str(uuid.uuid4())
    
    if session_id in sessions:
        del sessions[session_id]
        logger.info(f"Session deleted (request_id={request_id}, session_id={session_id})")
    
    return {
        "success": True,
        "session_id": session_id,
        "request_id": request_id
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )