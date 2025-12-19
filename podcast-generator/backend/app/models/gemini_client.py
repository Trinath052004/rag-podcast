from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class PodcastAgent(BaseModel):
    id: str
    name: str
    role: str
    personality: str
    voice_id: str

class PodcastMessage(BaseModel):
    agent_id: str
    content: str
    timestamp: datetime
    is_user_message: bool = False

class PodcastConversation(BaseModel):
    id: str
    pdf_id: str
    title: str
    agents: List[PodcastAgent]
    messages: List[PodcastMessage]
    status: str
    created_at: datetime
    updated_at: datetime

class GeminiGenerationRequest(BaseModel):
    pdf_id: str
    query: Optional[str] = None
    context: Optional[str] = None
    agent_configs: List[Dict[str, str]]

class GeminiGenerationResponse(BaseModel):
    conversation_id: str
    messages: List[PodcastMessage]
    status: str
    tokens_used: int
