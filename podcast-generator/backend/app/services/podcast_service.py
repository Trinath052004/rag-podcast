import uuid
from typing import List, Dict, Optional
from datetime import datetime
from app.services.pdf_service import PDFService
from app.services.gemini_service import GeminiService
from app.services.voice_service import VoiceService
from app.services.qdrant_service import QdrantService
from app.models.gemini_client import (
    PodcastConversation, PodcastAgent,
    GeminiGenerationRequest
)
from app.models.voice_interaction import CompletePodcastAudio
from app.models.pdf_processing import PDFProcessingResult
from app.config import settings
import logging

class PodcastService:
    def __init__(self):
        self.pdf_service = PDFService()
        self.gemini_service = GeminiService()
        self.voice_service = VoiceService()
        self.qdrant_service = QdrantService()
        self.logger = logging.getLogger(__name__)

    def generate_complete_podcast(self, pdf_file_path: str, filename: str, query: Optional[str] = None) -> Dict[str, Any]:
        """Generate a complete podcast from PDF file through all stages"""
        try:
            # Step 1: Process PDF file
            self.logger.info(f"Processing PDF file: {filename}")
            pdf_result = self.pdf_service.process_pdf_file(pdf_file_path, filename)

            # Step 2: Store vectors in Qdrant
            self.logger.info("Storing PDF chunks in Qdrant")
            self.qdrant_service.upsert_vectors(
                collection_name=settings.QDRANT_COLLECTION,
                chunks=pdf_result.chunks
            )

            # Step 3: Generate podcast conversation
            self.logger.info("Generating podcast conversation")
            conversation = self._generate_podcast_conversation(pdf_result.pdf_id, query)

            # Step 4: Generate podcast audio
            self.logger.info("Generating podcast audio")
            podcast_audio = self._generate_podcast_audio(conversation)

            # Step 5: Create complete podcast object
            complete_podcast = {
                "podcast_id": str(uuid.uuid4()),
                "pdf_id": pdf_result.pdf_id,
                "filename": filename,
                "title": conversation.title,
                "conversation": conversation.dict(),
                "audio": podcast_audio.dict(),
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "processing_steps": [
                    {"step": "PDF Processing", "status": "completed", "details": {
                        "total_chunks": pdf_result.total_chunks,
                        "total_pages": pdf_result.total_pages
                    }},
                    {"step": "Vector Storage", "status": "completed", "details": {
                        "collection": settings.QDRANT_COLLECTION,
                        "vectors_stored": pdf_result.total_chunks
                    }},
                    {"step": "Conversation Generation", "status": "completed", "details": {
                        "messages_generated": len(conversation.messages),
                        "agents": [agent.name for agent in conversation.agents]
                    }},
                    {"step": "Audio Generation", "status": "completed", "details": {
                        "segments_generated": len(podcast_audio.segments),
                        "total_duration": podcast_audio.total_duration
                    }}
                ]
            }

            return complete_podcast

        except Exception as e:
            self.logger.error(f"Error generating complete podcast: {str(e)}")
            raise Exception(f"Failed to generate complete podcast: {str(e)}")

    def _generate_podcast_conversation(self, pdf_id: str, query: Optional[str] = None) -> PodcastConversation:
        """Generate podcast conversation using Gemini"""
        # Default agent configurations
        default_agents = [
            {
                "name": "Dr. Knowledge",
                "role": "explainer",
                "personality": "Expert in the subject matter, patient, and thorough in explanations",
                "voice_id": "21m00Tcm4TlvDq8ikWAM"  # Default male voice
            },
            {
                "name": "Curious Carl",
                "role": "curious",
                "personality": "Inquisitive, asks insightful questions, represents the audience's perspective",
                "voice_id": "AZCnJ6YX1Dv9e0J9z4Jm"  # Default female voice
            },
            {
                "name": "You",
                "role": "user",
                "personality": "The actual user who can ask questions during the conversation",
                "voice_id": "EXAVITQu4vr4xnSDxMaL"  # Default user voice
            }
        ]

        # Create generation request
        generation_request = GeminiGenerationRequest(
            pdf_id=pdf_id,
            query=query or "Generate a podcast conversation about the PDF content",
            context=None,
            agent_configs=default_agents
        )

        # Generate conversation
        conversation = self.gemini_service.generate_podcast_conversation(generation_request)
        return conversation

    def _generate_podcast_audio(self, conversation: PodcastConversation) -> CompletePodcastAudio:
        """Generate audio for podcast conversation"""
        # Prepare messages for audio generation
        messages_for_audio = []
        for message in conversation.messages:
            # Find the agent for this message
            agent = next((a for a in conversation.agents if a.id == message.agent_id), None)
            if agent:
                messages_for_audio.append({
                    "agent_id": message.agent_id,
                    "content": message.content,
                    "voice_id": agent.voice_id
                })

        # Generate complete podcast audio
        podcast_audio = self.voice_service.generate_podcast_audio(
            conversation_id=conversation.id,
            messages=messages_for_audio
        )

        return podcast_audio

    def generate_podcast_with_rag(self, pdf_id: str, user_query: str) -> Dict[str, Any]:
        """Generate podcast response using RAG for a specific user query"""
        try:
            # Get the explainer agent (default configuration)
            explainer_agent = {
                "name": "Dr. Knowledge",
                "role": "explainer",
                "personality": "Expert in the subject matter, patient, and thorough in explanations",
                "voice_id": "21m00Tcm4TlvDq8ikWAM"
            }

            # Generate RAG response
            rag_response = self.gemini_service.generate_response_with_rag(
                pdf_id=pdf_id,
                query=user_query,
                agent=PodcastAgent(**explainer_agent)
            )

            # Generate audio for the response
            audio_request = {
                "text": rag_response,
                "voice_id": explainer_agent["voice_id"],
                "agent_id": "explainer",
                "format": "mp3"
            }

            audio_response = self.voice_service.generate_speech(audio_request)

            # Create response object
            response = {
                "response_id": str(uuid.uuid4()),
                "pdf_id": pdf_id,
                "query": user_query,
                "text_response": rag_response,
                "audio_response": audio_response.dict(),
                "agent": explainer_agent,
                "timestamp": datetime.now().isoformat()
            }

            return response

        except Exception as e:
            self.logger.error(f"Error generating RAG podcast response: {str(e)}")
            raise Exception(f"Failed to generate RAG podcast response: {str(e)}")

    def get_podcast_status(self, podcast_id: str) -> Dict[str, Any]:
        """Get status of podcast generation process"""
        # In a real implementation, this would check a database or cache
        # For now, return a sample status
        return {
            "podcast_id": podcast_id,
            "status": "completed",
            "progress": 100,
            "steps_completed": ["PDF Processing", "Vector Storage", "Conversation Generation", "Audio Generation"],
            "current_step": "completed",
            "timestamp": datetime.now().isoformat()
        }

    def list_user_podcasts(self, user_id: str) -> List[Dict[str, Any]]:
        """List all podcasts generated by a user"""
        # In a real implementation, this would query a database
        # For now, return sample data
        return [
            {
                "podcast_id": str(uuid.uuid4()),
                "title": "Sample Podcast 1",
                "pdf_name": "document.pdf",
                "created_at": "2023-01-01T10:00:00",
                "duration": 180.5,
                "status": "completed"
            },
            {
                "podcast_id": str(uuid.uuid4()),
                "title": "Sample Podcast 2",
                "pdf_name": "report.pdf",
                "created_at": "2023-01-02T11:30:00",
                "duration": 240.0,
                "status": "completed"
            }
        ]
