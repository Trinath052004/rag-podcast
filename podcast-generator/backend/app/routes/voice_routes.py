from fastapi import APIRouter, HTTPException, status, UploadFile, File
from typing import List, Optional
from app.services.voice_service import VoiceService
from app.models.voice_interaction import (
    AudioGenerationRequest, AudioGenerationResponse,
    VoiceInputRequest, VoiceInputResponse,
    CompletePodcastAudio
)
from app.config import settings
import base64

router = APIRouter()
voice_service = VoiceService()

@router.post("/generate", response_model=AudioGenerationResponse)
async def generate_speech(request: AudioGenerationRequest):
    """Generate speech from text using ElevenLabs TTS"""
    try:
        response = voice_service.generate_speech(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating speech: {str(e)}"
        )

@router.post("/process", response_model=VoiceInputResponse)
async def process_voice_input(
    audio_file: UploadFile = File(...),
    conversation_id: str = "default",
    user_id: str = "default"
):
    """Process voice input and convert to text"""
    try:
        # Read audio file content
        audio_content = await audio_file.read()

        # Encode as base64
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')

        # Create request
        request = VoiceInputRequest(
            audio_file=audio_base64,
            conversation_id=conversation_id,
            user_id=user_id
        )

        # Process voice input
        response = voice_service.process_voice_input(request)
        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing voice input: {str(e)}"
        )

@router.post("/podcast-audio", response_model=CompletePodcastAudio)
async def generate_podcast_audio(
    conversation_id: str,
    messages: List[dict]
):
    """Generate complete podcast audio from conversation messages"""
    try:
        response = voice_service.generate_podcast_audio(conversation_id, messages)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating podcast audio: {str(e)}"
        )

@router.get("/voices")
async def get_available_voices():
    """Get available voices from ElevenLabs"""
    try:
        voices = voice_service.get_available_voices()
        return {"voices": voices, "count": len(voices)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting available voices: {str(e)}"
        )

@router.post("/combine")
async def combine_audio_segments(
    segment_files: List[str],
    output_format: str = "mp3"
):
    """Combine multiple audio segments into a single file"""
    try:
        output_url = voice_service.combine_audio_segments(segment_files, output_format)
        return {"output_url": output_url, "format": output_format}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error combining audio segments: {str(e)}"
        )

@router.get("/podcasts/{podcast_id}/download")
async def download_podcast(podcast_id: str, format: str = "mp3"):
    """Generate download URL for a podcast"""
    try:
        download_url = voice_service.generate_podcast_download(podcast_id, format)
        return {"download_url": download_url, "format": format}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating podcast download: {str(e)}"
        )
