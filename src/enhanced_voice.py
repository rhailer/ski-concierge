import tempfile
import os
import time
import threading
from typing import Callable, Optional
import streamlit as st
from streamlit_audiorecorder import audiorecorder
import numpy as np
from config.settings import Config

class EnhancedVoiceHandler:
    def __init__(self, openai_client, on_transcription_callback: Callable[[str], None]):
        self.client = openai_client
        self.on_transcription = on_transcription_callback
        self.last_audio_hash = None
        self.conversation_active = False
        
    def render_voice_interface(self) -> bool:
        """
        Render an enhanced voice interface that feels continuous
        Returns True if new audio was processed
        """
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Enhanced visual feedback
            if not self.conversation_active:
                st.markdown("""
                <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #74b9ff, #0984e3); 
                           border-radius: 20px; color: white; margin: 1rem 0;'>
                    <h3 style='margin: 0; font-weight: 600;'>🎤 Ready to Chat!</h3>
                    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Click record and tell me about your skiing</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #00b894, #00a085); 
                           border-radius: 15px; color: white; margin: 1rem 0;'>
                    <h4 style='margin: 0;'>🎿 Let's keep talking! What else would you like to know?</h4>
                </div>
                """, unsafe_allow_html=True)
            
            # Audio recorder with enhanced styling
            audio = audiorecorder(
                start_prompt="🎤 Start Recording",
                stop_prompt="⏹️ Stop & Process",
                pause_prompt="⏸️ Pause",
                show_visualizer=True,
                key="main_recorder"
            )
            
            # Process new audio immediately
            if len(audio) > 0:
                # Create a simple hash to detect new recordings
                audio_hash = hash(bytes(audio.export().read()))
                
                if audio_hash != self.last_audio_hash:
                    self.last_audio_hash = audio_hash
                    
                    # Show immediate feedback
                    with st.spinner("🎧 Understanding what you said..."):
                        transcription = self._transcribe_audio(audio)
                        
                    if transcription:
                        # Show what was understood
                        st.success(f"✅ You said: *\"{transcription}\"*")
                        
                        # Process immediately
                        with st.spinner("🧠 Thinking about your perfect skis..."):
                            self.on_transcription(transcription)
                            self.conversation_active = True
                        
                        return True
            
            # Quick voice prompts for easier interaction
            st.markdown("### 💡 Try saying:")
            prompt_cols = st.columns(2)
            
            voice_prompts = [
                "I'm a beginner looking for my first skis",
                "I love skiing powder in Colorado",
                "I need carving skis under $500",
                "What's the difference between these options?"
            ]
            
            for i, prompt in enumerate(voice_prompts):
                col = prompt_cols[i % 2]
                with col:
                    if st.button(f"🗣️ \"{prompt}\"", key=f"prompt_{i}", help="Click to use this example"):
                        self.on_transcription(prompt)
                        return True
        
        return False
    
    def _transcribe_audio(self, audio) -> Optional[str]:
        """Transcribe audio using OpenAI Whisper"""
        try:
            # Export audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                audio.export(tmp_file.name, format="wav")
                
                # Transcribe with OpenAI
                with open(tmp_file.name, "rb") as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model=Config.VOICE_MODEL,
                        file=audio_file,
                        response_format="text"
                    )
                
                # Cleanup
                os.unlink(tmp_file.name)
                
                return transcript.strip() if transcript.strip() else None
                
        except Exception as e:
            st.error(f"Sorry, I couldn't understand that audio. Please try again. ({e})")
            return None
    
    def play_response(self, text: str):
        """Generate and play TTS response"""
        try:
            # Show that we're generating speech
            with st.spinner("🔊 Preparing voice response..."):
                response = self.client.audio.speech.create(
                    model=Config.TTS_MODEL,
                    voice=Config.TTS_VOICE,
                    input=text,
                    response_format="mp3"
                )
                
                # Auto-play the response
                st.audio(response.content, format="audio/mp3", autoplay=True)
                
                # Visual indicator that audio is playing
                st.info("🔊 Playing response... (Audio will play automatically)")
                
        except Exception as e:
            st.warning("Voice response not available, but here's my text response above!")