import tempfile
import os
import base64
import streamlit as st
from config.settings import Config

class SimpleVoiceHandler:
    def __init__(self, openai_client):
        self.client = openai_client
    
    def render_voice_interface(self):
        """Simple file upload based voice interface"""
        st.markdown("### 🎤 Voice Input")
        
        # Voice upload with clear instructions
        st.markdown("""
        **Record on your device and upload:**
        - Use your phone's voice recorder app
        - Or record on your computer (Voice Recorder on Windows, QuickTime on Mac)
        - Upload the audio file below
        """)
        
        uploaded_audio = st.file_uploader(
            "Upload your voice message",
            type=['mp3', 'wav', 'mp4', 'm4a', 'ogg'],
            help="Record a voice message and upload it here"
        )
        
        if uploaded_audio is not None:
            # Show audio player
            st.audio(uploaded_audio, format='audio/wav')
            
            # Process button
            if st.button("🎧 Process Voice Message", type="primary"):
                with st.spinner("🎧 Understanding what you said..."):
                    transcription = self._transcribe_uploaded_audio(uploaded_audio)
                    
                if transcription:
                    st.success(f"✅ You said: *\"{transcription}\"*")
                    return transcription
        
        return None
    
    def _transcribe_uploaded_audio(self, uploaded_file):
        """Transcribe uploaded audio file"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Transcribe with OpenAI
            with open(tmp_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=Config.VOICE_MODEL,
                    file=audio_file,
                    response_format="text"
                )
            
            # Cleanup
            os.unlink(tmp_file_path)
            
            return transcript.strip() if transcript.strip() else None
            
        except Exception as e:
            st.error(f"Error processing audio: {e}")
            return None
    
    def create_audio_response(self, text: str):
        """Create TTS audio response"""
        try:
            response = self.client.audio.speech.create(
                model=Config.TTS_MODEL,
                voice=Config.TTS_VOICE,
                input=text,
                response_format="mp3"
            )
            
            return response.content
            
        except Exception as e:
            st.error(f"Error creating voice response: {e}")
            return None
    
    def play_response(self, text: str):
        """Generate and display audio response"""
        try:
            with st.spinner("🔊 Creating voice response..."):
                audio_bytes = self.create_audio_response(text)
                
            if audio_bytes:
                st.markdown("### 🔊 My Response:")
                st.audio(audio_bytes, format="audio/mp3")
                st.success("🎧 Audio response ready! Click play above.")
            
        except Exception as e:
            st.warning("Voice response not available, but here's my text response!")