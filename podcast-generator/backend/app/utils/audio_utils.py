import os
import uuid
from pydub import AudioSegment
from pydub.effects import normalize
from typing import List, Optional
from app.config import settings
import logging

class AudioUtils:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        os.makedirs(settings.AUDIO_DIR, exist_ok=True)

    def convert_audio_format(self, input_path: str, output_format: str = "mp3") -> str:
        """Convert audio file to specified format"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(input_path)

            # Generate output filename
            filename = f"converted_{uuid.uuid4()}.{output_format}"
            output_path = os.path.join(settings.AUDIO_DIR, filename)

            # Export in new format
            audio.export(output_path, format=output_format)

            return output_path
        except Exception as e:
            self.logger.error(f"Error converting audio format: {str(e)}")
            raise Exception(f"Failed to convert audio: {str(e)}")

    def normalize_audio(self, input_path: str, target_dbfs: float = -20.0) -> str:
        """Normalize audio to target DBFS level"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(input_path)

            # Normalize audio
            change_in_dbfs = target_dbfs - audio.dBFS
            normalized = audio.apply_gain(change_in_dbfs)

            # Generate output filename
            filename = f"normalized_{uuid.uuid4()}.mp3"
            output_path = os.path.join(settings.AUDIO_DIR, filename)

            # Export normalized audio
            normalized.export(output_path, format="mp3")

            return output_path
        except Exception as e:
            self.logger.error(f"Error normalizing audio: {str(e)}")
            raise Exception(f"Failed to normalize audio: {str(e)}")

    def trim_silence(self, input_path: str, silence_thresh: int = -40, chunk_size: int = 10) -> str:
        """Trim silence from beginning and end of audio"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(input_path)

            # Trim silence
            trimmed = self._trim_silence(audio, silence_thresh, chunk_size)

            # Generate output filename
            filename = f"trimmed_{uuid.uuid4()}.mp3"
            output_path = os.path.join(settings.AUDIO_DIR, filename)

            # Export trimmed audio
            trimmed.export(output_path, format="mp3")

            return output_path
        except Exception as e:
            self.logger.error(f"Error trimming audio: {str(e)}")
            raise Exception(f"Failed to trim audio: {str(e)}")

    def _trim_silence(self, audio: AudioSegment, silence_thresh: int = -40, chunk_size: int = 10) -> AudioSegment:
        """Internal method to trim silence from audio"""
        # Trim leading silence
        start_trim = 0
        while start_trim < len(audio) and audio[start_trim:start_trim+chunk_size].dBFS < silence_thresh:
            start_trim += chunk_size

        # Trim trailing silence
        end_trim = len(audio)
        while end_trim > start_trim and audio[end_trim-chunk_size:end_trim].dBFS < silence_thresh:
            end_trim -= chunk_size

        return audio[start_trim:end_trim]

    def merge_audio_files(self, file_paths: List[str], output_format: str = "mp3") -> str:
        """Merge multiple audio files into one"""
        try:
            # Load all audio files
            audios = [AudioSegment.from_file(path) for path in file_paths]

            # Combine them
            combined = sum(audios)

            # Normalize the result
            combined = normalize(combined)

            # Generate output filename
            filename = f"merged_{uuid.uuid4()}.{output_format}"
            output_path = os.path.join(settings.AUDIO_DIR, filename)

            # Export merged audio
            combined.export(output_path, format=output_format)

            return output_path
        except Exception as e:
            self.logger.error(f"Error merging audio files: {str(e)}")
            raise Exception(f"Failed to merge audio files: {str(e)}")

    def add_intro_outro(self, main_audio_path: str, intro_path: Optional[str] = None, outro_path: Optional[str] = None) -> str:
        """Add intro and/or outro to audio file"""
        try:
            # Load main audio
            main_audio = AudioSegment.from_file(main_audio_path)

            # Add intro if provided
            if intro_path:
                intro = AudioSegment.from_file(intro_path)
                main_audio = intro + main_audio

            # Add outro if provided
            if outro_path:
                outro = AudioSegment.from_file(outro_path)
                main_audio = main_audio + outro

            # Generate output filename
            filename = f"final_{uuid.uuid4()}.mp3"
            output_path = os.path.join(settings.AUDIO_DIR, filename)

            # Export final audio
            main_audio.export(output_path, format="mp3")

            return output_path
        except Exception as e:
            self.logger.error(f"Error adding intro/outro: {str(e)}")
            raise Exception(f"Failed to add intro/outro: {str(e)}")

    def get_audio_duration(self, file_path: str) -> float:
        """Get duration of audio file in seconds"""
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0  # Convert milliseconds to seconds
        except Exception as e:
            self.logger.error(f"Error getting audio duration: {str(e)}")
            raise Exception(f"Failed to get audio duration: {str(e)}")

    def create_audio_preview(self, file_path: str, preview_length: int = 30) -> str:
        """Create a short preview of audio file"""
        try:
            audio = AudioSegment.from_file(file_path)

            # Take first 'preview_length' seconds
            preview_length_ms = preview_length * 1000
            preview = audio[:preview_length_ms]

            # Generate output filename
            filename = f"preview_{uuid.uuid4()}.mp3"
            output_path = os.path.join(settings.AUDIO_DIR, filename)

            # Export preview
            preview.export(output_path, format="mp3")

            return output_path
        except Exception as e:
            self.logger.error(f"Error creating audio preview: {str(e)}")
            raise Exception(f"Failed to create audio preview: {str(e)}")
