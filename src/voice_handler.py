import tempfile
import os
import sys
from io import BytesIO
import streamlit as st

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Config

class VoiceHandler:
    def __init__(self, openai_client):
        self.client = openai_client
        
    def transcribe_audio(self, audio_bytes) -> str:
        """
        Transcribe audio bytes to text using OpenAI Whisper
        """
        try:
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name
            
            # Transcribe using OpenAI Whisper
            with open(tmp_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=Config.VOICE_MODEL,
                    file=audio_file,
                    response_format="text"
                )
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            return transcript.strip()
            
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return "Sorry, I couldn't understand that. Could you try again?"
    
    def text_to_speech(self, text: str) -> bytes:
        """
        Convert text to speech using OpenAI TTS
        """
        try:
            response = self.client.audio.speech.create(
                model=Config.TTS_MODEL,
                voice=Config.TTS_VOICE,
                input=text,
                response_format="mp3"
            )
            
            return response.content
            
        except Exception as e:
            print(f"Error converting text to speech: {e}")
            return None
    
    def play_audio_response(self, text: str):
        """
        Generate and play audio response
        """
        audio_bytes = self.text_to_speech(text)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)