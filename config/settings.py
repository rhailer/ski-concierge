import os
from dotenv import load_dotenv

# Try to load .env file if it exists
try:
    load_dotenv()
except:
    pass

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = "gpt-4-turbo-preview"
    VOICE_MODEL = "whisper-1"
    TTS_MODEL = "tts-1"
    TTS_VOICE = "alloy"
    
    # Application settings
    APP_TITLE = "Ski Concierge - Your Personal Ski Expert"
    APP_ICON = "🎿"
    
    # Audio settings
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1
    MAX_RECORDING_DURATION = 60  # seconds