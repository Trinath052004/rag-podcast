from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from app.services.gemini_service import GeminiService
from app.models.gemini_client import (
    GeminiGenerationRequest, GeminiGenerationResponse,
    PodcastConversation, PodcastAgent
)
from app.config import settings

router = APIRouter()
gemini_service = GeminiService()

@router.post("/generate", response_model=GeminiGenerationResponse)
async def generate_podcast(request: GeminiGenerationRequest):
    """Generate a podcast conversation from PDF content"""
    try:
        # Generate podcast conversation
        conversation = gemini_service.generate_podcast_conversation(request)

        # Create response
        response = GeminiGenerationResponse(
            conversation_id=conversation.id,
            messages=conversation.messages,
            status="completed",
            tokens_used=len(" ".join([msg.content for msg in conversation.messages]).split())
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating podcast: {str(e)}"
        )

@router.get("/conversations/{conversation_id}", response_model=PodcastConversation)
async def get_conversation(conversation_id: str):
    """Get a specific podcast conversation"""
    # In a real implementation, this would retrieve from database
    # For now, return a sample conversation
    sample_agents = [
        PodcastAgent(
            id="1",
            name="Alex",
            role="explainer",
            personality="Knowledgeable and patient",
            voice_id="default"
        ),
        PodcastAgent(
            id="2",
            name="Jamie",
            role="curious",
            personality="Inquisitive and enthusiastic",
            voice_id="default"
        )
    ]

    sample_conversation = PodcastConversation(
        id=conversation_id,
        pdf_id="sample-pdf",
        title="Sample Podcast Conversation",
        agents=sample_agents,
        messages=[],
        status="completed",
        created_at="2023-01-01T00:00:00",
        updated_at="2023-01-01T00:00:00"
    )

    return sample_conversation

@router.post("/rag-response")
async def generate_rag_response(
    pdf_id: str,
    query: str,
    agent_role: str = "explainer"
):
    """Generate a response using RAG (Retrieval-Augmented Generation)"""
    try:
        # Create a temporary agent for the response
        agent = PodcastAgent(
            id="temp",
            name="Assistant",
            role=agent_role,
            personality="Helpful and informative",
            voice_id="default"
        )

        # Generate response using RAG
        response = gemini_service.generate_response_with_rag(pdf_id, query, agent)

        return {
            "response": response,
            "pdf_id": pdf_id,
            "query": query,
            "agent_role": agent_role
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating RAG response: {str(e)}"
        )

@router.get("/agents/default")
async def get_default_agents() -> List[PodcastAgent]:
    """Get default agent configurations"""
    default_agents = [
        {
            "name": "Dr. Knowledge",
            "role": "explainer",
            "personality": "Expert in the subject matter, patient, and thorough in explanations",
            "voice_id": "expert-male"
        },
        {
            "name": "Curious Carl",
            "role": "curious",
            "personality": "Inquisitive, asks insightful questions, represents the audience's perspective",
            "voice_id": "friendly-male"
        },
        {
            "name": "You",
            "role": "user",
            "personality": "The actual user who can ask questions during the conversation",
            "voice_id": "user-voice"
        }
    ]

    return default_agents
