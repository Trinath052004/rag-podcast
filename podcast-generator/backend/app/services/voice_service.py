import os
import uuid
from typing import List, Optional
from datetime import datetime
from elevenlabs import generate, save, set_api_key
from elevenlabs import voices as elevenlabs_voices
from pydub import AudioSegment
from pydub.effects import normalize
from app.models.voice_interaction import (
    AudioGenerationRequest, AudioGenerationResponse,
    PodcastAudioSegment, CompletePodcastAudio,
    VoiceInputRequest, VoiceInputResponse
)
from app.config import settings
import logging
import base64
import tempfile
import speech_recognition as sr

class VoiceService:
    def __init__(self):
        set_api_key(settings.ELEVENLABS_API_KEY)
        self.logger = logging.getLogger(__name__)
        os.makedirs(settings.AUDIO_DIR, exist_ok=True)

    def generate_speech(self, request: AudioGenerationRequest) -> AudioGenerationResponse:
        """Generate speech from text using ElevenLabs TTS"""
        try:
            # Generate audio
            audio = generate(
                text=request.text,
                voice=request.voice_id,
                model="eleven_multilingual_v1"
            )

            # Save audio file
            file_id = str(uuid.uuid4())
            filename = f"{file_id}.{request.format}"
            filepath = os.path.join(settings.AUDIO_DIR, filename)

            save(audio, filepath)

            # Get audio duration
            audio_segment = AudioSegment.from_file(filepath)
            duration = len(audio_segment) / 1000.0  # Convert to seconds

            # Create response
            response = AudioGenerationResponse(
                audio_url=f"/audio/{filename}",
                file_id=file_id,
                duration=duration,
                format=request.format
            )

            return response

        except Exception as e:
            self.logger.error(f"Error generating speech: {str(e)}")
            raise Exception(f"Failed to generate speech: {str(e)}")

    def process_voice_input(self, request: VoiceInputRequest) -> VoiceInputResponse:
        """Process voice input and convert to text"""
        try:
            # Decode audio file (assuming base64 encoded)
            audio_data = base64.b64decode(request.audio_file)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name

            # Use speech recognition
            recognizer = sr.Recognizer()

            with sr.AudioFile(temp_audio_path) as source:
                audio = recognizer.record(source)

            # Recognize speech
            text = recognizer.recognize_google(audio)

            # Clean up
            os.unlink(temp_audio_path)

            # Create response
            response = VoiceInputResponse(
                text=text,
                confidence=0.95,  # Approximate confidence
                language="en",
                processing_time=2.5  # Approximate processing time
            )

            return response

        except Exception as e:
            self.logger.error(f"Error processing voice input: {str(e)}")
            raise Exception(f"Failed to process voice input: {str(e)}")

    def generate_podcast_audio(self, conversation_id: str, messages: List[dict]) -> CompletePodcastAudio:
        """Generate complete podcast audio from conversation messages"""
        try:
            segments = []
            total_duration = 0.0

            # Generate audio for each message
            for i, message in enumerate(messages):
                # Get voice ID for agent (default to a standard voice)
                voice_id = message.get('voice_id', '21m00Tcm4TlvDq8ikWAM')

                # Create audio generation request
                audio_request = AudioGenerationRequest(
                    text=message['content'],
                    voice_id=voice_id,
                    agent_id=message['agent_id'],
                    format="mp3"
                )

                # Generate audio segment
                audio_response = self.generate_speech(audio_request)

                # Create podcast segment
                segment = PodcastAudioSegment(
                    segment_id=audio_response.file_id,
                    agent_id=message['agent_id'],
                    audio_url=audio_response.audio_url,
                    text_content=message['content'],
                    duration=audio_response.duration,
                    order=i
                )

                segments.append(segment)
                total_duration += audio_response.duration

            # Create complete podcast audio
            podcast_audio = CompletePodcastAudio(
                podcast_id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                segments=segments,
                total_duration=total_duration,
                format="mp3",
                download_url=f"/podcasts/{podcast_audio.podcast_id}/download"
            )

            return podcast_audio

        except Exception as e:
            self.logger.error(f"Error generating podcast audio: {str(e)}")
            raise Exception(f"Failed to generate podcast audio: {str(e)}")

    def combine_audio_segments(self, segment_files: List[str], output_format: str = "mp3") -> str:
        """Combine multiple audio segments into a single file"""
        try:
            # Load all segments
            combined = AudioSegment.silent(duration=0)

            for segment_file in segment_files:
                segment_path = os.path.join(settings.AUDIO_DIR, segment_file)
                segment = AudioSegment.from_file(segment_path)
                combined += segment

            # Normalize audio
            combined = normalize(combined)

            # Save combined audio
            output_id = str(uuid.uuid4())
            output_filename = f"podcast_{output_id}.{output_format}"
            output_path = os.path.join(settings.AUDIO_DIR, output_filename)

            combined.export(output_path, format=output_format)

            return f"/audio/{output_filename}"

        except Exception as e:
            self.logger.error(f"Error combining audio segments: {str(e)}")
            raise Exception(f"Failed to combine audio segments: {str(e)}")

    def get_available_voices(self) -> List[dict]:
        """Get available voices from ElevenLabs"""
        try:
            voices = elevenlabs_voices.get_all()
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category,
                    "labels": voice.labels
                }
                for voice in voices
            ]
        except Exception as e:
            self.logger.error(f"Error getting available voices: {str(e)}")
            return []

    def generate_podcast_download(self, podcast_id: str, format: str = "mp3") -> str:
        """Generate a downloadable podcast file"""
        try:
            # In a real implementation, this would:
            # 1. Find all audio segments for the podcast
            # 2. Combine them into a single file
            # 3. Return the download URL

            # For now, return a placeholder
            return f"/podcasts/{podcast_id}/download.{format}"

        except Exception as e:
            self.logger.error(f"Error generating podcast download: {str(e)}")
            raise Exception(f"Failed to generate podcast download: {str(e)}")
