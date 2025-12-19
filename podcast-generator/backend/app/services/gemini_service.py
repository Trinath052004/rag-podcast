import os
import google.generativeai as genai
from typing import List, Dict, Optional
from datetime import datetime
import uuid
from app.models.gemini_client import (
    PodcastAgent, PodcastMessage, PodcastConversation,
    GeminiGenerationRequest, GeminiGenerationResponse
)
from app.services.qdrant_service import QdrantService
from app.config import settings
import logging

class GeminiService:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        self.qdrant_service = QdrantService()
        self.logger = logging.getLogger(__name__)

    def generate_agent_response(self, agent: PodcastAgent, context: str, conversation_history: List[PodcastMessage]) -> str:
        """Generate a response for a specific agent based on context and conversation history"""
        try:
            # Prepare conversation history for prompt
            history_text = "\n".join(
                [f"{msg.agent_id}: {msg.content}" for msg in conversation_history[-5:]]  # Last 5 messages
            )

            # Create agent-specific prompt
            prompt = f"""
            You are {agent.name}, a {agent.role} with the following personality: {agent.personality}.
            Current conversation context: {context}
            Conversation history:
            {history_text}

            Please generate a response that is appropriate for your role and personality.
            Keep responses concise but informative, typically 1-3 sentences.
            """

            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            self.logger.error(f"Error generating agent response: {str(e)}")
            return f"Sorry, I encountered an error generating a response. {str(e)}"

    def generate_podcast_conversation(self, request: GeminiGenerationRequest) -> PodcastConversation:
        """Generate a complete podcast conversation based on PDF content"""
        try:
            # Initialize agents
            agents = []
            for agent_config in request.agent_configs:
                agent = PodcastAgent(
                    id=str(uuid.uuid4()),
                    name=agent_config["name"],
                    role=agent_config["role"],
                    personality=agent_config["personality"],
                    voice_id=agent_config.get("voice_id", "default")
                )
                agents.append(agent)

            # Get relevant context from Qdrant
            context = self._get_conversation_context(request.pdf_id, request.query)

            # Generate conversation
            messages = self._generate_conversation_flow(agents, context, request.query)

            # Create conversation object
            conversation = PodcastConversation(
                id=str(uuid.uuid4()),
                pdf_id=request.pdf_id,
                title=f"Podcast about {request.query or 'PDF content'}",
                agents=agents,
                messages=messages,
                status="completed",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            return conversation

        except Exception as e:
            self.logger.error(f"Error generating podcast conversation: {str(e)}")
            raise Exception(f"Failed to generate podcast conversation: {str(e)}")

    def _get_conversation_context(self, pdf_id: str, query: Optional[str] = None) -> str:
        """Get relevant context from Qdrant for conversation generation"""
        try:
            # Search for relevant chunks
            if query:
                # Generate embedding for query
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer('all-MiniLM-L6-v2')
                query_embedding = model.encode([query])[0].tolist()

                # Search in Qdrant
                results = self.qdrant_service.search_similar(
                    collection_name=settings.QDRANT_COLLECTION,
                    query_vector=query_embedding,
                    limit=5
                )

                # Extract relevant content
                context_chunks = [result.payload["content"] for result in results]
                context = "\n\n".join(context_chunks)
            else:
                # Get general context from the PDF
                context = f"Context from PDF {pdf_id} about various topics."

            return context

        except Exception as e:
            self.logger.error(f"Error getting conversation context: {str(e)}")
            return "General context about the PDF content."

    def _generate_conversation_flow(self, agents: List[PodcastAgent], context: str, query: Optional[str]) -> List[PodcastMessage]:
        """Generate a natural conversation flow between agents"""
        messages = []
        conversation_history = []

        # Find the explainer and curious agents
        explainer = next((a for a in agents if a.role == "explainer"), None)
        curious = next((a for a in agents if a.role == "curious"), None)
        user = next((a for a in agents if a.role == "user"), None)

        if not explainer or not curious:
            raise ValueError("Explainer and curious agents must be present")

        # Initial question from curious agent
        initial_question = f"What can you tell me about {query or 'this PDF content'}?"
        initial_message = PodcastMessage(
            agent_id=curious.id,
            content=initial_question,
            timestamp=datetime.now(),
            is_user_message=False
        )
        messages.append(initial_message)
        conversation_history.append(initial_message)

        # Generate 5-7 exchanges between agents
        for i in range(5):
            # Explainer responds to curious agent
            explainer_response = self.generate_agent_response(
                explainer, context, conversation_history
            )
            explainer_message = PodcastMessage(
                agent_id=explainer.id,
                content=explainer_response,
                timestamp=datetime.now(),
                is_user_message=False
            )
            messages.append(explainer_message)
            conversation_history.append(explainer_message)

            # Curious agent asks follow-up question
            followup_question = self.generate_agent_response(
                curious, context, conversation_history
            )
            followup_message = PodcastMessage(
                agent_id=curious.id,
                content=followup_question,
                timestamp=datetime.now(),
                is_user_message=False
            )
            messages.append(followup_message)
            conversation_history.append(followup_message)

        return messages

    def generate_response_with_rag(self, pdf_id: str, query: str, agent: PodcastAgent) -> str:
        """Generate a response using RAG (Retrieval-Augmented Generation)"""
        try:
            # Get relevant context from Qdrant
            context = self._get_conversation_context(pdf_id, query)

            # Generate response with context
            prompt = f"""
            You are {agent.name}, a {agent.role} with personality: {agent.personality}.
            Answer the following question based on the provided context:

            Question: {query}
            Context: {context}

            Provide a detailed and informative answer based on the context.
            If the context doesn't contain relevant information, say you don't know.
            """

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            self.logger.error(f"Error in RAG generation: {str(e)}")
            return f"Sorry, I couldn't generate a response based on the provided context. {str(e)}"
