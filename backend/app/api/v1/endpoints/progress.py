from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.services.progress_service import ProgressService
from app.schemas.progress import (
    SkillAssessment, 
    ProgressUpdate, 
    SkillHeatmap, 
    LearningRecommendation,
    TopicMastery,
    StudySession
)

router = APIRouter()


@router.get("/heatmap", response_model=SkillHeatmap)
async def get_skill_heatmap(
    subject: str = None,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get visual skill heatmap showing mastery levels across topics.
    
    Returns:
    - Topics organized by subject/category
    - Mastery levels (Not Started, Learning, Practiced, Mastered)
    - Difficulty ratings and time estimates
    - Learning dependencies between topics
    """
    progress_service = ProgressService(db)
    heatmap = await progress_service.generate_skill_heatmap(subject=subject)
    return heatmap


@router.get("/recommendations", response_model=List[LearningRecommendation])
async def get_learning_recommendations(
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get personalized learning recommendations based on:
    - Current skill gaps
    - Learning objectives
    - Previously struggled topics
    - Prerequisite dependencies
    """
    progress_service = ProgressService(db)
    recommendations = await progress_service.generate_recommendations(limit=limit)
    return recommendations


@router.post("/assess-skill")
async def assess_skill(
    assessment: SkillAssessment,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Record a skill assessment (e.g., quiz result, problem solution).
    
    This updates the user's progress and adjusts future recommendations.
    """
    progress_service = ProgressService(db)
    await progress_service.record_skill_assessment(assessment)
    return {"message": "Skill assessment recorded successfully"}


@router.post("/update-progress")
async def update_progress(
    progress: ProgressUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    """Update user's progress on a specific topic or concept."""
    progress_service = ProgressService(db)
    await progress_service.update_topic_progress(progress)
    return {"message": "Progress updated successfully"}


@router.get("/topics/{topic_id}/mastery", response_model=TopicMastery)
async def get_topic_mastery(
    topic_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    """Get detailed mastery information for a specific topic."""
    progress_service = ProgressService(db)
    mastery = await progress_service.get_topic_mastery(topic_id)
    
    if not mastery:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return mastery


@router.get("/analytics", response_model=Dict[str, Any])
async def get_learning_analytics(
    days: int = 30,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get comprehensive learning analytics including:
    - Study time trends
    - Progress velocity
    - Strength/weakness analysis
    - Goal completion rates
    """
    progress_service = ProgressService(db)
    analytics = await progress_service.generate_analytics(days=days)
    return analytics


@router.post("/study-session")
async def record_study_session(
    session: StudySession,
    db: AsyncSession = Depends(get_async_session),
):
    """Record a study session for progress tracking."""
    progress_service = ProgressService(db)
    await progress_service.record_study_session(session)
    return {"message": "Study session recorded successfully"}


@router.get("/study-sessions", response_model=List[StudySession])
async def get_study_sessions(
    days: int = 30,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session),
):
    """Get recent study sessions."""
    progress_service = ProgressService(db)
    sessions = await progress_service.get_study_sessions(
        days=days, skip=skip, limit=limit
    )
    return sessions


@router.get("/streak")
async def get_study_streak(
    db: AsyncSession = Depends(get_async_session),
):
    """Get current study streak and related statistics."""
    progress_service = ProgressService(db)
    streak = await progress_service.calculate_study_streak()
    return streak


@router.get("/goals", response_model=List[Dict[str, Any]])
async def get_learning_goals(
    active_only: bool = True,
    db: AsyncSession = Depends(get_async_session),
):
    """Get user's learning goals and progress towards them."""
    progress_service = ProgressService(db)
    goals = await progress_service.get_learning_goals(active_only=active_only)
    return goals


@router.post("/goals")
async def create_learning_goal(
    goal: Dict[str, Any],
    db: AsyncSession = Depends(get_async_session),
):
    """Create a new learning goal."""
    progress_service = ProgressService(db)
    created_goal = await progress_service.create_learning_goal(goal)
    return created_goal


@router.get("/difficulty-analysis")
async def get_difficulty_analysis(
    subject: str = None,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Analyze which topics/concepts the user finds most challenging.
    
    Useful for:
    - Identifying areas needing more practice
    - Adjusting study plans
    - Providing targeted resources
    """
    progress_service = ProgressService(db)
    analysis = await progress_service.analyze_difficulty_patterns(subject=subject)
    return analysis
