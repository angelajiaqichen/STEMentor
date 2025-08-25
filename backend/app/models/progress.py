from datetime import datetime, date
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class MasteryLevel(str, Enum):
    NOT_STARTED = "not_started"
    LEARNING = "learning"
    PRACTICING = "practicing"
    MASTERED = "mastered"


class AssessmentType(str, Enum):
    QUIZ = "quiz"
    PROBLEM_SOLVING = "problem_solving"
    DISCUSSION = "discussion"
    SELF_ASSESSMENT = "self_assessment"
    AI_EVALUATION = "ai_evaluation"


class ProgressRecord(Base):
    __tablename__ = "progress_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    
    # Progress metrics
    mastery_level = Column(SQLEnum(MasteryLevel), default=MasteryLevel.NOT_STARTED)
    confidence_score = Column(Float, default=0.0)  # 0.0 to 1.0
    time_spent_minutes = Column(Integer, default=0)
    
    # Performance tracking
    total_attempts = Column(Integer, default=0)
    successful_attempts = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # calculated field
    
    # Learning velocity
    first_attempt_at = Column(DateTime(timezone=True), nullable=True)
    last_practice_at = Column(DateTime(timezone=True), nullable=True)
    mastery_achieved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Difficulty and engagement
    perceived_difficulty = Column(Float, nullable=True)  # 1.0 (easy) to 5.0 (very hard)
    engagement_level = Column(Float, nullable=True)  # 1.0 (bored) to 5.0 (very engaged)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="progress_records")
    topic = relationship("Topic", back_populates="progress_records")
    assessments = relationship("SkillAssessmentRecord", back_populates="progress_record")
    
    def __repr__(self):
        return f"<ProgressRecord(user_id={self.user_id}, topic_id={self.topic_id}, mastery='{self.mastery_level}')>"


class SkillAssessmentRecord(Base):
    __tablename__ = "skill_assessment_records"

    id = Column(Integer, primary_key=True, index=True)
    progress_record_id = Column(Integer, ForeignKey("progress_records.id"), nullable=False)
    
    # Assessment details
    assessment_type = Column(SQLEnum(AssessmentType), nullable=False)
    question_or_task = Column(Text, nullable=True)
    user_response = Column(Text, nullable=True)
    
    # Performance metrics
    score = Column(Float, nullable=True)  # 0.0 to 1.0 or specific scoring system
    max_score = Column(Float, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    
    # Timing
    time_taken_seconds = Column(Integer, nullable=True)
    attempts_before_success = Column(Integer, default=1)
    
    # AI feedback and analysis
    ai_feedback = Column(Text, nullable=True)
    identified_weaknesses = Column(JSON, default=[])
    suggested_improvements = Column(JSON, default=[])
    
    # Context
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    progress_record = relationship("ProgressRecord", back_populates="assessments")
    conversation = relationship("Conversation")
    document = relationship("Document")
    
    def __repr__(self):
        return f"<SkillAssessmentRecord(id={self.id}, type='{self.assessment_type}', score={self.score})>"


class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session details
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    subject = Column(String, nullable=True)
    
    # Timing
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)  # calculated field
    
    # Content covered
    topics_studied = Column(JSON, default=[])  # List of topic IDs
    documents_reviewed = Column(JSON, default=[])  # List of document IDs
    conversations_had = Column(JSON, default=[])  # List of conversation IDs
    
    # Session metrics
    focus_score = Column(Float, nullable=True)  # Subjective focus level 1-5
    difficulty_encountered = Column(Float, nullable=True)  # Average difficulty 1-5
    satisfaction = Column(Float, nullable=True)  # How satisfied with progress 1-5
    
    # Goals and outcomes
    session_goals = Column(JSON, default=[])  # What user wanted to accomplish
    goals_achieved = Column(JSON, default=[])  # What was actually accomplished
    notes = Column(Text, nullable=True)  # User's session notes
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="study_sessions")
    
    def __repr__(self):
        return f"<StudySession(id={self.id}, user_id={self.user_id}, duration={self.duration_minutes}min)>"


class LearningGoal(Base):
    __tablename__ = "learning_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Goal definition
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String, nullable=True)
    
    # Goal specifics
    target_topics = Column(JSON, default=[])  # List of topic IDs to master
    target_mastery_level = Column(SQLEnum(MasteryLevel), default=MasteryLevel.MASTERED)
    estimated_duration_days = Column(Integer, nullable=True)
    
    # Timeline
    target_date = Column(Date, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Progress tracking
    is_active = Column(Boolean, default=True)
    progress_percentage = Column(Float, default=0.0)  # 0.0 to 100.0
    
    # Motivation and tracking
    motivation_level = Column(Float, nullable=True)  # 1-5 scale
    priority = Column(String, default="medium")  # low, medium, high
    reminder_frequency = Column(String, nullable=True)  # daily, weekly, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<LearningGoal(id={self.id}, title='{self.title}', progress={self.progress_percentage}%)>"


class StreakRecord(Base):
    __tablename__ = "streak_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Streak details
    streak_date = Column(Date, nullable=False)
    study_minutes = Column(Integer, default=0)
    topics_practiced = Column(Integer, default=0)
    conversations_count = Column(Integer, default=0)
    
    # Quality metrics
    focus_quality = Column(Float, nullable=True)  # Average focus for the day
    learning_satisfaction = Column(Float, nullable=True)
    
    # Milestones
    is_milestone = Column(Boolean, default=False)  # 7, 30, 100 day milestones
    milestone_type = Column(String, nullable=True)  # "weekly", "monthly", "hundred_day"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<StreakRecord(user_id={self.user_id}, date={self.streak_date}, minutes={self.study_minutes})>"
