from typing import List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.services.chat_service import ChatService
from app.schemas.chat import ChatMessage, ChatResponse, ConversationCreate, ConversationResponse

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    db: AsyncSession = Depends(get_async_session),
):
    """Create a new chat conversation."""
    chat_service = ChatService(db)
    return await chat_service.create_conversation(conversation)


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session),
):
    """List all chat conversations."""
    chat_service = ChatService(db)
    return await chat_service.get_conversations(skip=skip, limit=limit)


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    """Get a specific conversation by ID."""
    chat_service = ChatService(db)
    conversation = await chat_service.get_conversation_by_id(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: int,
    message: ChatMessage,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Send a message to the AI tutor and get a response.
    
    The AI tutor has access to:
    - All uploaded documents and their analysis
    - Previous conversation history
    - User's learning progress and skill gaps
    """
    chat_service = ChatService(db)
    
    # Verify conversation exists
    conversation = await chat_service.get_conversation_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Process message and generate response
    response = await chat_service.process_message(conversation_id, message)
    
    return response


@router.get("/conversations/{conversation_id}/messages", response_model=List[ChatResponse])
async def get_conversation_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session),
):
    """Get all messages in a conversation."""
    chat_service = ChatService(db)
    
    # Verify conversation exists
    conversation = await chat_service.get_conversation_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await chat_service.get_conversation_messages(
        conversation_id, skip=skip, limit=limit
    )
    
    return messages


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    """Delete a conversation and all its messages."""
    chat_service = ChatService(db)
    success = await chat_service.delete_conversation(conversation_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"message": "Conversation deleted successfully"}


@router.websocket("/conversations/{conversation_id}/ws")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    """
    WebSocket endpoint for real-time chat with the AI tutor.
    
    Supports streaming responses and real-time interaction.
    """
    await websocket.accept()
    chat_service = ChatService(db)
    
    try:
        # Verify conversation exists
        conversation = await chat_service.get_conversation_by_id(conversation_id)
        if not conversation:
            await websocket.send_json({
                "type": "error",
                "message": "Conversation not found"
            })
            await websocket.close()
            return
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data["type"] == "message":
                message = ChatMessage(**data["content"])
                
                # Process message with streaming response
                async for chunk in chat_service.process_message_stream(conversation_id, message):
                    await websocket.send_json({
                        "type": "response_chunk",
                        "content": chunk
                    })
                
                # Send final response
                response = await chat_service.get_last_response(conversation_id)
                await websocket.send_json({
                    "type": "response_complete",
                    "content": response
                })
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        await websocket.close()


@router.post("/conversations/{conversation_id}/feedback")
async def provide_feedback(
    conversation_id: int,
    message_id: int,
    feedback: dict,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Provide feedback on an AI response to improve future interactions.
    
    Feedback can include:
    - Rating (1-5 stars)
    - Helpful/Not helpful
    - Comments for improvement
    """
    chat_service = ChatService(db)
    
    await chat_service.save_feedback(conversation_id, message_id, feedback)
    
    return {"message": "Feedback saved successfully"}
