import asyncio
from typing import List, Optional, AsyncGenerator, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate

from app.models.chat import Conversation, Message, MessageRole
from app.models.document import Document
from app.models.progress import ProgressRecord
from app.core.config import settings
from app.schemas.chat import ConversationCreate, ChatMessage


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = OpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
            max_tokens=1000
        ) if settings.OPENAI_API_KEY else None
        
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY
        ) if settings.OPENAI_API_KEY else None

    async def create_conversation(self, conversation_data: ConversationCreate) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            user_id=1,  # TODO: Get from current user
            title=conversation_data.title,
            description=conversation_data.description,
            subject=conversation_data.subject,
            context_documents=conversation_data.context_documents or [],
            learning_objectives=conversation_data.learning_objectives or [],
            difficulty_level=conversation_data.difficulty_level
        )
        
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        
        return conversation

    async def get_conversations(self, skip: int = 0, limit: int = 100) -> List[Conversation]:
        """Get list of conversations."""
        result = await self.db.execute(
            select(Conversation)
            .offset(skip)
            .limit(limit)
            .order_by(Conversation.last_activity_at.desc())
        )
        return result.scalars().all()

    async def get_conversation_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """Get a specific conversation by ID."""
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def process_message(self, conversation_id: int, message: ChatMessage) -> Dict:
        """Process a user message and generate AI response."""
        conversation = await self.get_conversation_by_id(conversation_id)
        if not conversation:
            raise Exception("Conversation not found")

        # Save user message
        user_message = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=message.content,
            message_type=message.message_type or "general"
        )
        self.db.add(user_message)

        # Generate AI response
        ai_response_content = await self._generate_ai_response(
            conversation, message.content
        )

        # Save AI response
        ai_message = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=ai_response_content,
            model_used="gpt-3.5-turbo",
            message_type="response"
        )
        self.db.add(ai_message)

        # Update conversation metadata
        conversation.total_messages += 2
        conversation.last_activity_at = user_message.created_at

        await self.db.commit()
        await self.db.refresh(ai_message)

        return {
            "id": ai_message.id,
            "role": ai_message.role,
            "content": ai_message.content,
            "created_at": ai_message.created_at,
            "message_type": ai_message.message_type
        }

    async def get_conversation_messages(
        self, conversation_id: int, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        """Get messages in a conversation."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .offset(skip)
            .limit(limit)
            .order_by(Message.created_at.asc())
        )
        return result.scalars().all()

    async def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation and all its messages."""
        conversation = await self.get_conversation_by_id(conversation_id)
        if not conversation:
            return False

        await self.db.delete(conversation)
        await self.db.commit()
        return True

    async def save_feedback(self, conversation_id: int, message_id: int, feedback: Dict):
        """Save user feedback on an AI response."""
        result = await self.db.execute(
            select(Message).where(
                Message.id == message_id,
                Message.conversation_id == conversation_id
            )
        )
        message = result.scalar_one_or_none()
        
        if message:
            message.user_rating = feedback.get("rating")
            message.user_feedback = feedback.get("comments")
            message.is_helpful = feedback.get("is_helpful")
            await self.db.commit()

    async def process_message_stream(
        self, conversation_id: int, message: ChatMessage
    ) -> AsyncGenerator[str, None]:
        """Process message with streaming response."""
        # This would implement streaming responses for real-time chat
        # For now, we'll simulate streaming by yielding chunks
        response = await self._generate_ai_response_simple(message.content)
        
        # Simulate streaming by yielding chunks
        words = response.split()
        for i, word in enumerate(words):
            if i > 0:
                yield " "
            yield word
            await asyncio.sleep(0.05)  # Simulate typing delay

    async def get_last_response(self, conversation_id: int) -> Optional[Dict]:
        """Get the last AI response in a conversation."""
        result = await self.db.execute(
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.role == MessageRole.ASSISTANT
            )
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        message = result.scalar_one_or_none()
        
        if message:
            return {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at
            }
        return None

    async def _generate_ai_response(self, conversation: Conversation, user_input: str) -> str:
        """Generate AI response with context awareness."""
        if not self.llm:
            return "I'm sorry, but I'm not configured to provide AI responses. Please check the API configuration."

        # Build context from conversation history, documents, and user progress
        context = await self._build_context(conversation)
        
        # Create a contextualized prompt
        prompt_template = self._get_tutor_prompt_template(conversation)
        
        try:
            # Generate response using the AI model
            full_prompt = prompt_template.format(
                context=context,
                user_input=user_input,
                conversation_history=await self._get_conversation_history(conversation.id),
                learning_objectives=", ".join(conversation.learning_objectives),
                difficulty_level=conversation.difficulty_level or "intermediate"
            )
            
            response = await asyncio.to_thread(self.llm, full_prompt)
            return response.strip()
            
        except Exception as e:
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"

    async def _generate_ai_response_simple(self, user_input: str) -> str:
        """Simple AI response without full context (for streaming demo)."""
        if not self.llm:
            return "I'm sorry, but I'm not configured to provide AI responses."

        try:
            prompt = f"As a helpful AI tutor, please respond to this student question: {user_input}"
            response = await asyncio.to_thread(self.llm, prompt)
            return response.strip()
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"

    async def _build_context(self, conversation: Conversation) -> str:
        """Build contextual information for the AI response."""
        context_parts = []

        # Add document context
        if conversation.context_documents:
            for doc_id in conversation.context_documents:
                doc = await self._get_document_context(doc_id)
                if doc:
                    context_parts.append(f"Document: {doc}")

        # Add user progress context
        progress_context = await self._get_user_progress_context(conversation.user_id)
        if progress_context:
            context_parts.append(f"User Progress: {progress_context}")

        return "\n\n".join(context_parts) if context_parts else ""

    async def _get_document_context(self, document_id: int) -> Optional[str]:
        """Get relevant context from a document."""
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if document and document.ai_analysis:
            # Extract key information from the document analysis
            analysis = document.ai_analysis
            context = f"Title: {document.title}\n"
            if "summary" in analysis:
                context += f"Summary: {analysis['summary']}\n"
            if "key_concepts" in analysis:
                context += f"Key Concepts: {', '.join(analysis['key_concepts'])}\n"
            return context
        
        return None

    async def _get_user_progress_context(self, user_id: int) -> Optional[str]:
        """Get user's learning progress context."""
        # Get recent progress records
        result = await self.db.execute(
            select(ProgressRecord)
            .where(ProgressRecord.user_id == user_id)
            .order_by(ProgressRecord.updated_at.desc())
            .limit(10)
        )
        progress_records = result.scalars().all()
        
        if progress_records:
            context = "Recent learning progress:\n"
            for record in progress_records:
                context += f"- Topic {record.topic_id}: {record.mastery_level} (confidence: {record.confidence_score})\n"
            return context
        
        return None

    async def _get_conversation_history(self, conversation_id: int, limit: int = 10) -> str:
        """Get recent conversation history."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        
        history = []
        for message in reversed(messages):
            role = "Student" if message.role == MessageRole.USER else "Tutor"
            history.append(f"{role}: {message.content}")
        
        return "\n".join(history)

    def _get_tutor_prompt_template(self, conversation: Conversation) -> PromptTemplate:
        """Get the AI tutor prompt template."""
        template = """
You are an intelligent AI tutor helping a student learn. You have access to their uploaded materials and learning progress.

Context Information:
{context}

Conversation History:
{conversation_history}

Learning Objectives:
{learning_objectives}

Difficulty Level: {difficulty_level}

Student's Question/Input:
{user_input}

Instructions:
1. Provide helpful, educational responses that guide the student to understanding
2. Use the context from their uploaded materials when relevant
3. Adapt your explanation to the specified difficulty level
4. If they're struggling with a concept, break it down into simpler parts
5. Encourage critical thinking by asking follow-up questions when appropriate
6. Reference their progress and previously covered material when relevant

Response:
"""
        
        return PromptTemplate(
            input_variables=["context", "conversation_history", "learning_objectives", 
                           "difficulty_level", "user_input"],
            template=template
        )
