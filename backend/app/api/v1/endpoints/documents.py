from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.services.document_service import DocumentService
from app.services.content_extraction_service import ContentExtractionService
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentAnalysis

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = None,
    subject: str = None,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Upload a document (PDF, DOCX, TXT, etc.) for processing.
    
    The document will be processed in the background to extract:
    - Topics and subtopics
    - Key formulas and equations
    - Definitions and theorems
    - Problem types and complexity levels
    """
    doc_service = DocumentService(db)
    
    # Validate file type and size
    if not await doc_service.validate_file(file):
        raise HTTPException(status_code=400, detail="Invalid file type or size")
    
    # Create document record
    document_data = DocumentCreate(
        title=title or file.filename,
        filename=file.filename,
        content_type=file.content_type,
        subject=subject
    )
    
    document = await doc_service.create_document(document_data, file)
    
    # Process document in background
    background_tasks.add_task(
        process_document_content,
        document.id,
        db
    )
    
    return document


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    subject: str = None,
    db: AsyncSession = Depends(get_async_session),
):
    """List all uploaded documents with optional filtering by subject."""
    doc_service = DocumentService(db)
    documents = await doc_service.get_documents(skip=skip, limit=limit, subject=subject)
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    """Get a specific document by ID."""
    doc_service = DocumentService(db)
    document = await doc_service.get_document_by_id(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.get("/{document_id}/analysis", response_model=DocumentAnalysis)
async def get_document_analysis(
    document_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    """Get the AI analysis results for a document."""
    doc_service = DocumentService(db)
    analysis = await doc_service.get_document_analysis(document_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found or still processing")
    
    return analysis


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
):
    """Reprocess a document with updated AI analysis."""
    doc_service = DocumentService(db)
    document = await doc_service.get_document_by_id(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Reprocess document in background
    background_tasks.add_task(
        process_document_content,
        document_id,
        db
    )
    
    return {"message": "Document reprocessing started"}


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    """Delete a document and all associated data."""
    doc_service = DocumentService(db)
    success = await doc_service.delete_document(document_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document deleted successfully"}


async def process_document_content(document_id: int, db: AsyncSession):
    """Background task to process document content with AI."""
    content_service = ContentExtractionService()
    doc_service = DocumentService(db)
    
    try:
        # Extract and analyze content
        analysis = await content_service.process_document(document_id)
        
        # Save analysis results
        await doc_service.save_document_analysis(document_id, analysis)
        
    except Exception as e:
        # Log error and mark document as failed
        await doc_service.mark_processing_failed(document_id, str(e))
