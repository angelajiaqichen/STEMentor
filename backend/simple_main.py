from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import time
from datetime import datetime

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

@app.post("/api/v1/chat/test")
def chat_test():
    return {
        "message": "Chat endpoint ready!",
        "response": "Hello! I'm your AI tutor. Once configured with OpenAI API, I'll be able to help you learn by analyzing your documents and providing personalized assistance.",
        "status": "mock_response"
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
