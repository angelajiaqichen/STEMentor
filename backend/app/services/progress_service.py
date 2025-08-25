import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from collections import defaultdict

from app.models.progress import (
    ProgressRecord, MasteryLevel, SkillAssessmentRecord, 
    StudySession, LearningGoal, StreakRecord
)
from app.models.document import Topic
from app.models.user import User
from app.schemas.progress import SkillAssessment, ProgressUpdate


class ProgressService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_skill_heatmap(self, subject: Optional[str] = None) -> Dict[str, Any]:
        """Generate a visual skill heatmap showing mastery levels across topics."""
        # Get user's progress records
        query = select(ProgressRecord).join(Topic).where(ProgressRecord.user_id == 1)  # TODO: Get from current user
        
        if subject:
            query = query.where(Topic.subject == subject)
        
        result = await self.db.execute(query)
        progress_records = result.scalars().all()
        
        # Organize data by subject and topic
        heatmap_data = defaultdict(lambda: defaultdict(dict))
        
        for record in progress_records:
            topic_query = await self.db.execute(
                select(Topic).where(Topic.id == record.topic_id)
            )
            topic = topic_query.scalar_one_or_none()
            
            if topic:
                subject_name = topic.subject or "General"
                heatmap_data[subject_name][topic.title] = {
                    "mastery_level": record.mastery_level.value,
                    "confidence_score": record.confidence_score,
                    "time_spent_minutes": record.time_spent_minutes,
                    "success_rate": record.success_rate,
                    "difficulty": topic.difficulty_level or "intermediate",
                    "last_practice": record.last_practice_at.isoformat() if record.last_practice_at else None
                }
        
        # Convert to structured format for frontend
        structured_heatmap = []
        for subject_name, topics in heatmap_data.items():
            subject_data = {
                "subject": subject_name,
                "topics": []
            }
            
            for topic_name, data in topics.items():
                subject_data["topics"].append({
                    "name": topic_name,
                    "mastery": data["mastery_level"],
                    "confidence": data["confidence_score"],
                    "time_spent": data["time_spent_minutes"],
                    "success_rate": data["success_rate"],
                    "difficulty": data["difficulty"],
                    "last_practice": data["last_practice"]
                })
            
            structured_heatmap.append(subject_data)
        
        return {
            "heatmap": structured_heatmap,
            "summary": {
                "total_topics": sum(len(s["topics"]) for s in structured_heatmap),
                "mastered_topics": sum(
                    len([t for t in s["topics"] if t["mastery"] == "mastered"]) 
                    for s in structured_heatmap
                ),
                "in_progress_topics": sum(
                    len([t for t in s["topics"] if t["mastery"] in ["learning", "practicing"]]) 
                    for s in structured_heatmap
                )
            }
        }

    async def generate_recommendations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Generate personalized learning recommendations."""
        recommendations = []
        
        # Get user's current progress
        result = await self.db.execute(
            select(ProgressRecord).where(ProgressRecord.user_id == 1)  # TODO: Get from current user
        )
        progress_records = result.scalars().all()
        
        # Identify areas for improvement
        struggling_topics = [
            record for record in progress_records 
            if record.success_rate < 0.7 or record.confidence_score < 0.6
        ]
        
        for record in struggling_topics[:limit]:
            topic_result = await self.db.execute(
                select(Topic).where(Topic.id == record.topic_id)
            )
            topic = topic_result.scalar_one_or_none()
            
            if topic:
                recommendations.append({
                    "type": "review",
                    "priority": "high" if record.success_rate < 0.5 else "medium",
                    "topic_id": topic.id,
                    "topic_title": topic.title,
                    "reason": f"Low success rate ({record.success_rate:.1%})",
                    "suggested_action": "Review fundamentals and practice problems",
                    "estimated_time_minutes": 45
                })
        
        # Suggest next topics based on prerequisites
        ready_topics = await self._find_topics_ready_for_learning()
        for topic in ready_topics[:limit - len(recommendations)]:
            recommendations.append({
                "type": "new_topic",
                "priority": "medium",
                "topic_id": topic.id,
                "topic_title": topic.title,
                "reason": "Prerequisites completed",
                "suggested_action": "Start learning this new topic",
                "estimated_time_minutes": topic.estimated_time_minutes or 60
            })
        
        return recommendations

    async def record_skill_assessment(self, assessment: SkillAssessment):
        """Record a skill assessment and update progress."""
        # Find or create progress record
        result = await self.db.execute(
            select(ProgressRecord).where(
                and_(
                    ProgressRecord.user_id == 1,  # TODO: Get from current user
                    ProgressRecord.topic_id == assessment.topic_id
                )
            )
        )
        progress_record = result.scalar_one_or_none()
        
        if not progress_record:
            progress_record = ProgressRecord(
                user_id=1,  # TODO: Get from current user
                topic_id=assessment.topic_id
            )
            self.db.add(progress_record)
        
        # Create assessment record
        assessment_record = SkillAssessmentRecord(
            progress_record_id=progress_record.id,
            assessment_type=assessment.assessment_type,
            question_or_task=assessment.question,
            user_response=assessment.user_response,
            score=assessment.score,
            max_score=assessment.max_score,
            is_correct=assessment.is_correct,
            time_taken_seconds=assessment.time_taken_seconds
        )
        self.db.add(assessment_record)
        
        # Update progress metrics
        progress_record.total_attempts += 1
        if assessment.is_correct:
            progress_record.successful_attempts += 1
        
        progress_record.success_rate = progress_record.successful_attempts / progress_record.total_attempts
        progress_record.last_practice_at = datetime.utcnow()
        
        # Update mastery level based on performance
        await self._update_mastery_level(progress_record)
        
        await self.db.commit()

    async def update_topic_progress(self, progress: ProgressUpdate):
        """Update user's progress on a specific topic."""
        result = await self.db.execute(
            select(ProgressRecord).where(
                and_(
                    ProgressRecord.user_id == 1,  # TODO: Get from current user
                    ProgressRecord.topic_id == progress.topic_id
                )
            )
        )
        progress_record = result.scalar_one_or_none()
        
        if not progress_record:
            progress_record = ProgressRecord(
                user_id=1,  # TODO: Get from current user
                topic_id=progress.topic_id
            )
            self.db.add(progress_record)
        
        # Update fields
        if progress.mastery_level:
            progress_record.mastery_level = progress.mastery_level
        if progress.confidence_score is not None:
            progress_record.confidence_score = progress.confidence_score
        if progress.time_spent_minutes:
            progress_record.time_spent_minutes += progress.time_spent_minutes
        if progress.perceived_difficulty is not None:
            progress_record.perceived_difficulty = progress.perceived_difficulty
        
        progress_record.last_practice_at = datetime.utcnow()
        
        await self.db.commit()

    async def get_topic_mastery(self, topic_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed mastery information for a specific topic."""
        result = await self.db.execute(
            select(ProgressRecord).where(
                and_(
                    ProgressRecord.user_id == 1,  # TODO: Get from current user
                    ProgressRecord.topic_id == topic_id
                )
            )
        )
        progress_record = result.scalar_one_or_none()
        
        if not progress_record:
            return None
        
        # Get topic info
        topic_result = await self.db.execute(
            select(Topic).where(Topic.id == topic_id)
        )
        topic = topic_result.scalar_one_or_none()
        
        if not topic:
            return None
        
        # Get recent assessments
        assessments_result = await self.db.execute(
            select(SkillAssessmentRecord)
            .where(SkillAssessmentRecord.progress_record_id == progress_record.id)
            .order_by(SkillAssessmentRecord.created_at.desc())
            .limit(10)
        )
        recent_assessments = assessments_result.scalars().all()
        
        return {
            "topic": {
                "id": topic.id,
                "title": topic.title,
                "description": topic.description,
                "difficulty_level": topic.difficulty_level
            },
            "progress": {
                "mastery_level": progress_record.mastery_level.value,
                "confidence_score": progress_record.confidence_score,
                "time_spent_minutes": progress_record.time_spent_minutes,
                "success_rate": progress_record.success_rate,
                "total_attempts": progress_record.total_attempts,
                "successful_attempts": progress_record.successful_attempts
            },
            "recent_assessments": [
                {
                    "type": assessment.assessment_type.value,
                    "score": assessment.score,
                    "is_correct": assessment.is_correct,
                    "created_at": assessment.created_at.isoformat()
                }
                for assessment in recent_assessments
            ]
        }

    async def generate_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive learning analytics."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get study sessions in the period
        sessions_result = await self.db.execute(
            select(StudySession).where(
                and_(
                    StudySession.user_id == 1,  # TODO: Get from current user
                    StudySession.start_time >= start_date
                )
            )
        )
        study_sessions = sessions_result.scalars().all()
        
        # Calculate metrics
        total_study_time = sum(s.duration_minutes or 0 for s in study_sessions)
        average_session_length = total_study_time / len(study_sessions) if study_sessions else 0
        
        # Progress velocity (topics advanced per day)
        progress_result = await self.db.execute(
            select(ProgressRecord).where(
                and_(
                    ProgressRecord.user_id == 1,  # TODO: Get from current user
                    ProgressRecord.last_practice_at >= start_date
                )
            )
        )
        active_topics = progress_result.scalars().all()
        
        return {
            "period": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "study_time": {
                "total_minutes": total_study_time,
                "average_session_minutes": round(average_session_length, 1),
                "sessions_count": len(study_sessions),
                "daily_average_minutes": round(total_study_time / days, 1)
            },
            "progress": {
                "active_topics": len(active_topics),
                "topics_mastered": len([t for t in active_topics if t.mastery_level == MasteryLevel.MASTERED]),
                "topics_in_progress": len([t for t in active_topics if t.mastery_level in [MasteryLevel.LEARNING, MasteryLevel.PRACTICING]])
            },
            "performance": {
                "average_success_rate": sum(t.success_rate for t in active_topics) / len(active_topics) if active_topics else 0,
                "average_confidence": sum(t.confidence_score for t in active_topics) / len(active_topics) if active_topics else 0
            }
        }

    async def record_study_session(self, session_data: Dict[str, Any]):
        """Record a study session."""
        session = StudySession(
            user_id=1,  # TODO: Get from current user
            title=session_data.get("title"),
            description=session_data.get("description"),
            subject=session_data.get("subject"),
            start_time=datetime.fromisoformat(session_data["start_time"]),
            end_time=datetime.fromisoformat(session_data["end_time"]) if session_data.get("end_time") else None,
            duration_minutes=session_data.get("duration_minutes"),
            topics_studied=session_data.get("topics_studied", []),
            documents_reviewed=session_data.get("documents_reviewed", []),
            focus_score=session_data.get("focus_score"),
            satisfaction=session_data.get("satisfaction"),
            session_goals=session_data.get("session_goals", []),
            goals_achieved=session_data.get("goals_achieved", []),
            notes=session_data.get("notes")
        )
        
        self.db.add(session)
        await self.db.commit()

    async def get_study_sessions(
        self, days: int = 30, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent study sessions."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        result = await self.db.execute(
            select(StudySession)
            .where(
                and_(
                    StudySession.user_id == 1,  # TODO: Get from current user
                    StudySession.start_time >= start_date
                )
            )
            .order_by(StudySession.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        sessions = result.scalars().all()
        
        return [
            {
                "id": session.id,
                "title": session.title,
                "subject": session.subject,
                "start_time": session.start_time.isoformat(),
                "duration_minutes": session.duration_minutes,
                "focus_score": session.focus_score,
                "satisfaction": session.satisfaction,
                "topics_count": len(session.topics_studied)
            }
            for session in sessions
        ]

    async def calculate_study_streak(self) -> Dict[str, Any]:
        """Calculate current study streak and related statistics."""
        # This is a simplified implementation
        # In practice, you'd want to check daily study activity
        
        current_date = date.today()
        streak_days = 0
        longest_streak = 0
        
        # Check consecutive days with study activity
        for i in range(365):  # Check last year
            check_date = current_date - timedelta(days=i)
            
            # Check if user studied on this date
            sessions_result = await self.db.execute(
                select(StudySession).where(
                    and_(
                        StudySession.user_id == 1,  # TODO: Get from current user
                        func.date(StudySession.start_time) == check_date
                    )
                )
            )
            has_activity = sessions_result.scalars().first() is not None
            
            if has_activity:
                streak_days += 1
                longest_streak = max(longest_streak, streak_days)
            else:
                if i == 0:  # Today has no activity
                    break
                elif streak_days > 0:  # Previous streak ended
                    break
        
        return {
            "current_streak": streak_days,
            "longest_streak": longest_streak,
            "streak_maintained": streak_days > 0
        }

    async def _find_topics_ready_for_learning(self) -> List[Topic]:
        """Find topics that are ready to be learned based on prerequisites."""
        # Get all topics
        all_topics_result = await self.db.execute(select(Topic))
        all_topics = all_topics_result.scalars().all()
        
        # Get user's mastered topics
        mastered_result = await self.db.execute(
            select(ProgressRecord).where(
                and_(
                    ProgressRecord.user_id == 1,  # TODO: Get from current user
                    ProgressRecord.mastery_level == MasteryLevel.MASTERED
                )
            )
        )
        mastered_topic_ids = {record.topic_id for record in mastered_result.scalars()}
        
        ready_topics = []
        for topic in all_topics:
            # Check if all prerequisites are met
            prerequisites = topic.prerequisites or []
            if all(prereq_id in mastered_topic_ids for prereq_id in prerequisites):
                # Check if not already started
                if topic.id not in mastered_topic_ids:
                    ready_topics.append(topic)
        
        return ready_topics

    async def _update_mastery_level(self, progress_record: ProgressRecord):
        """Update mastery level based on performance metrics."""
        success_rate = progress_record.success_rate
        confidence = progress_record.confidence_score
        attempts = progress_record.total_attempts
        
        if attempts >= 5 and success_rate >= 0.9 and confidence >= 0.8:
            progress_record.mastery_level = MasteryLevel.MASTERED
            if not progress_record.mastery_achieved_at:
                progress_record.mastery_achieved_at = datetime.utcnow()
        elif attempts >= 3 and success_rate >= 0.7:
            progress_record.mastery_level = MasteryLevel.PRACTICING
        elif attempts >= 1:
            progress_record.mastery_level = MasteryLevel.LEARNING
        else:
            progress_record.mastery_level = MasteryLevel.NOT_STARTED
