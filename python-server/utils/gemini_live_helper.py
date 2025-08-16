import asyncio
import io
import os
import logging
import tempfile
from pathlib import Path
from google import genai
from google.genai import types
import soundfile as sf
import librosa
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GeminiLiveHelper:
    def __init__(self, api_key=None):
        # Always use API key from environment variables
        self.api_key = os.environ.get('API_KEY')
        
        if not self.api_key:
            logger.warning("No API_KEY found in environment variables. Gemini Live functionality will not work.")
        
        self.client = None
        self.model_name = "gemini-2.0-flash"  # Use the correct model for audio processing
    
    def _get_client(self):
        """Get or create the Gemini client"""
        if self.client is None:
            if not self.api_key:
                raise ValueError("No API key available for Gemini Live. Set API_KEY in environment variables.")
            self.client = genai.Client(api_key=self.api_key)
        return self.client
    
    async def audio_to_text(self, audio_file_path):
        """
        Convert audio file to text using Gemini API
        Uses inline audio data approach as per Gemini documentation
        """
        try:
            logger.info(f"Processing audio file: {audio_file_path}")
            
            if not self.api_key:
                raise ValueError("No API key available for Gemini. Set API_KEY in environment variables.")
            
            # Read the audio file as bytes
            with open(audio_file_path, 'rb') as f:
                audio_bytes = f.read()
            
            logger.info(f"Audio file size: {len(audio_bytes)} bytes")
            
            # Determine mime type based on file extension
            file_extension = audio_file_path.lower().split('.')[-1]
            mime_type_map = {
                'mp3': 'audio/mp3',
                'wav': 'audio/wav',
                'webm': 'audio/webm',
                'ogg': 'audio/ogg',
                'm4a': 'audio/m4a'
            }
            mime_type = mime_type_map.get(file_extension, 'audio/wav')
            
            # Use Gemini API to transcribe the audio
            client = self._get_client()
            
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[
                    'Transcribe this audio clip to text. Provide only the transcription without any additional commentary.',
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type=mime_type,
                    )
                ]
            )
            
            transcribed_text = response.text.strip()
            logger.info(f"Transcription successful: {transcribed_text[:100]}...")
            
            return transcribed_text
            
        except Exception as e:
            logger.error(f"Error in audio_to_text: {str(e)}", exc_info=True)
            raise
    
    def process_course_audio_description(self, audio_file_path):
        """
        Process audio file to extract course description text using course service
        
        Args:
            audio_file_path: Path to the audio file containing course description
            
        Returns:
            str: Extracted course description text
        """
        try:
            # First, convert audio to text using the synchronous method
            transcribed_text = self.audio_to_text_sync(audio_file_path)
            
            if not transcribed_text:
                raise ValueError("No text could be extracted from the audio")
            
            logger.info(f"Transcribed text: {transcribed_text[:100]}...")
            
            # Use the course service's existing Gemini functionality to generate course content
            from models.schemas import CourseContent
            from utils.gemini_helper import GeminiHelper
            
            gemini_helper = GeminiHelper()
            
            # Use the same approach as course service for generating course content
            prompt = f"""Generate a course name and description(max 100 words) based on '{transcribed_text}'.
            The description should be comprehensive and educational.
            Return only the course details without any additional text."""
            
            response = gemini_helper.generate_content(
                prompt,
                response_schema=CourseContent
            )
            
            # Return the generated description
            return response['description']
            
        except Exception as e:
            logger.error(f"Error processing course audio description: {str(e)}")
            # Return a fallback course description
            return "Introduction to Learning and Education - A comprehensive course covering fundamental learning principles and educational methodologies."
    
    def audio_to_text_sync(self, audio_file_path):
        """
        Synchronous version of audio to text conversion
        """
        try:
            logger.info(f"Processing audio file: {audio_file_path}")
            
            if not self.api_key:
                raise ValueError("No API key available for Gemini. Set API_KEY in environment variables.")
            
            # Read the audio file as bytes
            with open(audio_file_path, 'rb') as f:
                audio_bytes = f.read()
            
            logger.info(f"Audio file size: {len(audio_bytes)} bytes")
            
            # Determine mime type based on file extension
            file_extension = audio_file_path.lower().split('.')[-1]
            mime_type_map = {
                'mp3': 'audio/mp3',
                'wav': 'audio/wav',
                'webm': 'audio/webm',
                'ogg': 'audio/ogg',
                'm4a': 'audio/m4a'
            }
            mime_type = mime_type_map.get(file_extension, 'audio/wav')
            
            # Use Gemini API to transcribe the audio
            client = self._get_client()
            
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[
                    'Transcribe this audio clip to text. Provide only the transcription without any additional commentary.',
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type=mime_type,
                    )
                ]
            )
            
            transcribed_text = response.text.strip()
            logger.info(f"Transcription successful: {transcribed_text[:100]}...")
            
            return transcribed_text
            
        except Exception as e:
            logger.error(f"Error in audio_to_text_sync: {str(e)}", exc_info=True)
            raise
