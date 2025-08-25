from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import time
from datetime import datetime
from pydantic import BaseModel
import logging
from services.ai_service import ai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    context: str = None
    system_message: str = None

class ChatResponse(BaseModel):
    response: str
    model_info: dict = None
    status: str = "success"

app = FastAPI(
    title="STEMentor API",
    version="1.0.0",
    description="AI-powered learning platform with intelligent content processing"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
async def root():
    return {
        "message": "🎓 Welcome to STEMentor - AI Learning Platform!",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "Document Upload & Processing",
            "AI-Powered Content Analysis", 
            "Smart Chatbot Tutor",
            "Progress Tracking & Heatmaps"
        ],
        "docs": "/docs"
    }

@app.get("/api/v1/documents")
def get_documents():
    return {
        "message": "Documents endpoint ready!",
        "status": "mock_data",
        "documents": [
            {
                "id": 1,
                "title": "Sample Machine Learning Notes",
                "subject": "Computer Science",
                "status": "processed"
            }
        ]
    }

@app.post("/api/v1/documents/upload")
async def upload_document(
    file: UploadFile = File(...), 
    subject: str = Form(...)
):
    """Upload a document for processing"""
    
    # Validate file type
    allowed_types = [
        'application/pdf', 
        'text/plain', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword'
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail="File type not supported. Please upload PDF, TXT, or DOCX files."
        )
    
    # Generate unique filename
    timestamp = int(time.time())
    file_path = UPLOAD_DIR / f"{timestamp}_{file.filename}"
    
    try:
        # Read and save file
        contents = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Create document record
        document_data = {
            "id": timestamp,
            "title": file.filename,
            "subject": subject,
            "status": "uploaded",
            "file_path": str(file_path),
            "upload_time": datetime.now().isoformat(),
            "file_size": len(contents),
            "content_type": file.content_type
        }
        
        return {
            "message": "Document uploaded successfully!",
            "document": document_data,
            "status": "success"
        }
        
    except Exception as e:
        # Clean up file if something goes wrong
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the AI service on startup"""
    logger.info("Starting STEMentor API...")
    try:
        await ai_service.initialize()
        logger.info("AI service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AI service: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    logger.info("Shutting down STEMentor API...")

# Chat endpoints
@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat with the Llama 3 AI tutor"""
    try:
        logger.info(f"Received chat request: {request.message[:100]}...")
        
        response = await ai_service.generate_response(
            user_message=request.message,
            context=request.context,
            system_message=request.system_message
        )
        
        model_info = await ai_service.get_model_info()
        
        return ChatResponse(
            response=response,
            model_info=model_info,
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate response: {str(e)}"
        )

@app.post("/api/v1/chat/test")
async def chat_test():
    """Test endpoint for the AI chat - uses a simple predefined message"""
    try:
        if not ai_service.is_initialized:
            return {
                "message": "Chat endpoint ready!",
                "response": "AI service is initializing. Please wait a moment and try again.",
                "status": "initializing"
            }
        
        response = await ai_service.generate_response(
            "Hello! Can you introduce yourself as an AI tutor and explain what subjects you can help with?"
        )
        
        model_info = await ai_service.get_model_info()
        
        return {
            "message": "Chat test successful!",
            "response": response,
            "status": "success",
            "model_info": model_info
        }
        
    except Exception as e:
        logger.error(f"Chat test error: {str(e)}")
        return {
            "message": "Chat endpoint ready!",
            "response": f"AI service encountered an error: {str(e)}. Using fallback response.",
            "status": "error"
        }

@app.get("/api/v1/ai/status")
async def get_ai_status():
    """Get the status of the AI service"""
    model_info = await ai_service.get_model_info()
    return {
        "ai_service_status": "initialized" if ai_service.is_initialized else "not_initialized",
        "model_info": model_info
    }

@app.get("/api/v1/progress/test")  
def get_progress():
    return {
        "heatmap": {
            "Mathematics": {
                "Calculus": "mastered",
                "Linear Algebra": "practicing", 
                "Statistics": "learning"
            },
            "Physics": {
                "Mechanics": "mastered",
                "Thermodynamics": "practicing",
                "Quantum Physics": "learning"
            }
        },
        "overall_progress": 65
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
