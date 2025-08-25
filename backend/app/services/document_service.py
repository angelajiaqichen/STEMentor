import os
import uuid
from typing import Optional, List
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.document import Document, ProcessingStatus
from app.core.config import settings
from app.schemas.document import DocumentCreate


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate_file(self, file: UploadFile) -> bool:
        """Validate uploaded file type and size."""
        # Check file size
        if file.size and file.size > settings.MAX_UPLOAD_SIZE:
            return False
        
        # Check file extension
        if file.filename:
            extension = file.filename.split('.')[-1].lower()
            if extension not in settings.ALLOWED_EXTENSIONS:
                return False
        
        return True

    async def create_document(self, document_data: DocumentCreate, file: UploadFile) -> Document:
        """Create a new document record and save the file."""
        # Generate unique filename
        file_extension = file.filename.split('.')[-1].lower() if file.filename else 'txt'
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(settings.UPLOAD_FOLDER, unique_filename)
        
        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create document record
        document = Document(
            user_id=1,  # TODO: Get from current user
            title=document_data.title,
            filename=unique_filename,
            original_filename=file.filename or "unknown",
            file_path=file_path,
            content_type=file.content_type or "application/octet-stream",
            file_size=len(content),
            subject=document_data.subject,
            processing_status=ProcessingStatus.PENDING
        )
        
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        
        return document

    async def get_documents(self, skip: int = 0, limit: int = 100, subject: Optional[str] = None) -> List[Document]:
        """Get list of documents with optional filtering."""
        query = select(Document).offset(skip).limit(limit)
        
        if subject:
            query = query.where(Document.subject == subject)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """Get a specific document by ID."""
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def get_document_analysis(self, document_id: int) -> Optional[dict]:
        """Get AI analysis results for a document."""
        document = await self.get_document_by_id(document_id)
        if not document or not document.ai_analysis:
            return None
        return document.ai_analysis

    async def save_document_analysis(self, document_id: int, analysis: dict):
        """Save AI analysis results for a document."""
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if document:
            document.ai_analysis = analysis
            document.processing_status = ProcessingStatus.COMPLETED
            await self.db.commit()

    async def mark_processing_failed(self, document_id: int, error_message: str):
        """Mark document processing as failed."""
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if document:
            document.processing_status = ProcessingStatus.FAILED
            document.processing_error = error_message
            await self.db.commit()

    async def delete_document(self, document_id: int) -> bool:
        """Delete a document and its file."""
        document = await self.get_document_by_id(document_id)
        if not document:
            return False
        
        # Delete file from disk
        try:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
        except Exception:
            pass  # Continue even if file deletion fails
        
        # Delete database record
        await self.db.delete(document)
        await self.db.commit()
        
        return True
