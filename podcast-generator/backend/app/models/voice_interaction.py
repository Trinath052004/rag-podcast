from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class VoiceInputRequest(BaseModel):
    audio_file: str  # Base64 encoded audio or file path
    conversation_id: str
    user_id: str

class VoiceInputResponse(BaseModel):
    text: str
    confidence: float
    language: str
    processing_time: float

class AudioGenerationRequest(BaseModel):
    text: str
    voice_id: str
    agent_id: str
    format: str = "mp3"

class AudioGenerationResponse(BaseModel):
    audio_url: str
    file_id: str
    duration: float
    format: str

class PodcastAudioSegment(BaseModel):
    segment_id: str
    agent_id: str
    audio_url: str
    text_content: str
    duration: float
    order: int

class CompletePodcastAudio(BaseModel):
    podcast_id: str
    conversation_id: str
    segments: List[PodcastAudioSegment]
    total_duration: float
    format: str
    download_url: str
