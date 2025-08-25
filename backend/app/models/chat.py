from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Conversation metadata
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String, nullable=True)  # math, physics, chemistry, etc.
    
    # Context and settings
    context_documents = Column(JSON, default=[])  # List of document IDs for context
    learning_objectives = Column(JSON, default=[])  # What the user wants to learn
    difficulty_level = Column(String, nullable=True)  # beginner, intermediate, advanced
    
    # Conversation state
    is_active = Column(Boolean, default=True)
    total_messages = Column(Integer, default=0)
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
    
    # AI Tutor settings
    tutor_personality = Column(String, default="helpful")  # helpful, encouraging, challenging
    explanation_style = Column(String, default="detailed")  # brief, detailed, step-by-step
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}', messages={self.total_messages})>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    
    # Message content
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    
    # Message metadata
    token_count = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    # AI specific fields
    model_used = Column(String, nullable=True)  # gpt-4, claude-3, etc.
    temperature = Column(Float, nullable=True)
    
    # Context and references
    referenced_documents = Column(JSON, default=[])  # Documents referenced in this message
    referenced_topics = Column(JSON, default=[])  # Topics discussed
    code_snippets = Column(JSON, default=[])  # Any code examples or formulas
    
    # User interaction
    user_rating = Column(Integer, nullable=True)  # 1-5 star rating
    user_feedback = Column(Text, nullable=True)
    is_helpful = Column(Boolean, nullable=True)
    
    # Message features
    contains_math = Column(Boolean, default=False)
    contains_code = Column(Boolean, default=False)
    message_type = Column(String, default="general")  # general, explanation, problem_solving, quiz
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', type='{self.message_type}')>"


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    
    # Summary content
    summary = Column(Text, nullable=False)
    key_topics_covered = Column(JSON, default=[])
    learning_progress = Column(JSON, default={})  # Topics learned/practiced
    unresolved_questions = Column(JSON, default=[])
    
    # Summary metadata
    message_range_start = Column(Integer, nullable=False)  # First message ID in summary
    message_range_end = Column(Integer, nullable=False)  # Last message ID in summary
    generated_by_ai = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation")
    
    def __repr__(self):
        return f"<ConversationSummary(id={self.id}, conversation_id={self.conversation_id})>"
