from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File information
    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    
    # Content and metadata
    subject = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    extracted_text = Column(Text, nullable=True)
    
    # Processing status
    processing_status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    processing_error = Column(Text, nullable=True)
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # AI Analysis results
    ai_analysis = Column(JSON, nullable=True)  # Stores extracted topics, formulas, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="documents")
    topics = relationship("Topic", back_populates="document", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', status='{self.processing_status}')>"


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    # Topic information
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String, nullable=True)
    difficulty_level = Column(String, nullable=True)  # beginner, intermediate, advanced
    estimated_time_minutes = Column(Integer, nullable=True)
    
    # Hierarchical structure
    parent_topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    order_index = Column(Integer, default=0)
    
    # Content
    content = Column(Text, nullable=True)
    formulas = Column(JSON, default=[])  # List of formulas with explanations
    definitions = Column(JSON, default=[])  # Key definitions and terms
    examples = Column(JSON, default=[])  # Examples and practice problems
    
    # Learning metadata
    prerequisites = Column(JSON, default=[])  # List of prerequisite topic IDs
    learning_objectives = Column(JSON, default=[])
    common_mistakes = Column(JSON, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="topics")
    parent_topic = relationship("Topic", remote_side=[id], backref="subtopics")
    progress_records = relationship("ProgressRecord", back_populates="topic")
    
    def __repr__(self):
        return f"<Topic(id={self.id}, title='{self.title}', subject='{self.subject}')>"


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Note content
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    note_type = Column(String, default="general")  # general, summary, flashcard, etc.
    
    # AI generated notes metadata
    is_ai_generated = Column(Boolean, default=False)
    source_topics = Column(JSON, default=[])  # List of topic IDs this note covers
    
    # Organization
    tags = Column(JSON, default=[])
    is_favorite = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="notes")
    user = relationship("User")
    
    def __repr__(self):
        return f"<Note(id={self.id}, title='{self.title}', ai_generated={self.is_ai_generated})>"
