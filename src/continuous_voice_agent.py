import streamlit as st
from streamlit_mic_recorder import mic_recorder
import tempfile
import os
import time
import threading
from typing import Callable
from config.settings import Config

class ContinuousVoiceAgent:
    def __init__(self, openai_client, on_voice_callback: Callable[[str], str]):
        self.client = openai_client
        self.on_voice_callback = on_voice_callback
        self.is_listening = False
        self.conversation_active = False
        
    def start_continuous_conversation(self):
        """Start the continuous voice conversation interface"""
        
        # Conversation status indicator
        if not self.conversation_active:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
                       padding: 2rem; border-radius: 20px; text-align: center; margin: 2rem 0;
                       animation: fadeIn 0.5s ease-in;'>
                <h2 style='margin: 0 0 1rem 0;'>🎤 Ready for Continuous Voice Dialog</h2>
                <p style='margin: 0; font-size: 1.2rem; opacity: 0.9;'>
                    Start talking and I'll respond naturally - just like a real conversation!
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #00b894, #00a085); color: white; 
                       padding: 1.5rem; border-radius: 15px; text-align: center; margin: 1rem 0;
                       animation: pulse 2s infinite;'>
                <h3 style='margin: 0;'>🗣️ Conversation Active - Keep Talking!</h3>
            </div>
            """, unsafe_allow_html=True)
        
        # Continuous voice interface
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Main voice interface - this should be continuous
            audio = mic_recorder(
                start_prompt="🎤 Start Talking",
                stop_prompt="⏸️ Pause",
                just_once=False,  # This is key - allows continuous recording
                use_container_width=True,
                callback=self._handle_audio_chunk,
                args=(),
                kwargs={},
                key="continuous_voice_recorder"
            )
            
            # Process audio immediately when received
            if audio is not None and len(audio['bytes']) > 0:
                self._process_continuous_audio(audio['bytes'])
        
        # Quick voice commands for natural flow
        if self.conversation_active:
            st.markdown("### 💡 Try saying:")
            
            quick_commands = [
                "Tell me more about that first option",
                "What's the difference between these skis?", 
                "Help me choose between these",
                "Show me something cheaper",
                "What about for powder skiing?",
                "I need help with sizing"
            ]
            
            command_cols = st.columns(3)
            for i, command in enumerate(quick_commands):
                col = command_cols[i % 3]
                with col:
                    if st.button(f"🗣️ \"{command}\"", key=f"voice_cmd_{i}"):
                        self._simulate_voice_input(command)
    
    def _handle_audio_chunk(self, audio_data):
        """Handle continuous audio chunks"""
        if audio_data and len(audio_data) > 100:  # Only process if we have meaningful audio
            # Process in background to maintain flow
            threading.Thread(
                target=self._process_audio_chunk_async,
                args=(audio_data,),
                daemon=True
            ).start()
    
    def _process_audio_chunk_async(self, audio_bytes):
        """Process audio chunk asynchronously"""
        try:
            transcription = self._transcribe_audio_bytes(audio_bytes)
            if transcription and len(transcription.strip()) > 3:  # Meaningful speech
                # Get AI response
                ai_response = self.on_voice_callback(transcription)
                
                # Update UI state
                st.session_state.last_transcription = transcription
                st.session_state.last_ai_response = ai_response
                st.session_state.should_play_response = True
                st.session_state.conversation_active = True
                
        except Exception as e:
            print(f"Error in async audio processing: {e}")
    
    def _process_continuous_audio(self, audio_bytes):
        """Process audio for continuous dialog"""
        if not audio_bytes or len(audio_bytes) < 100:
            return
        
        # Show processing indicator
        with st.spinner("🎧 Listening..."):
            transcription = self._transcribe_audio_bytes(audio_bytes)
        
        if transcription and len(transcription.strip()) > 2:
            # Show what was heard
            st.success(f"👂 Heard: *\"{transcription}\"*")
            
            # Get AI response immediately
            with st.spinner("🧠 Thinking..."):
                ai_response = self.on_voice_callback(transcription)
            
            # Display text response
            st.markdown(f"""
            <div style='background: #f8f9fa; padding: 1.5rem; border-radius: 15px; 
                       border-left: 4px solid #007bff; margin: 1rem 0;'>
                <strong>🎿 Ski Concierge:</strong> {ai_response}
            </div>
            """, unsafe_allow_html=True)
            
            # Play voice response immediately
            self._play_immediate_response(ai_response)
            
            # Mark conversation as active
            self.conversation_active = True
            st.session_state.conversation_active = True
    
    def _transcribe_audio_bytes(self, audio_bytes) -> str:
        """Transcribe audio bytes using OpenAI Whisper"""
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name
            
            # Transcribe
            with open(tmp_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=Config.VOICE_MODEL,
                    file=audio_file,
                    response_format="text"
                )
            
            # Cleanup
            os.unlink(tmp_file_path)
            
            return transcript.strip() if transcript else ""
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    def _play_immediate_response(self, text: str):
        """Play AI response immediately for continuous flow"""
        try:
            # Generate TTS
            response = self.client.audio.speech.create(
                model=Config.TTS_MODEL,
                voice=Config.TTS_VOICE,
                input=text[:1000],  # Keep responses concise for flow
                response_format="mp3"
            )
            
            # Play immediately
            st.audio(response.content, format="audio/mp3", autoplay=True)
            
            # Encourage continuation
            st.info("🎤 **Keep talking!** I'm listening for your next question...")
            
        except Exception as e:
            st.warning("Voice response not available, but I'm still listening!")
    
    def _simulate_voice_input(self, text: str):
        """Simulate voice input for testing"""
        st.info(f"🗣️ Simulating: *\"{text}\"*")
        
        # Process as if it was voice
        with st.spinner("🧠 Processing..."):
            ai_response = self.on_voice_callback(text)
        
        # Display response
        st.success(f"🎿 {ai_response}")
        
        # Play voice response
        self._play_immediate_response(ai_response)
        
        self.conversation_active = True
        st.session_state.conversation_active = True

def create_voice_agent_interface(openai_client, voice_callback):
    """Create the continuous voice agent interface"""
    
    # Initialize voice agent
    if 'voice_agent' not in st.session_state:
        st.session_state.voice_agent = ContinuousVoiceAgent(openai_client, voice_callback)
    
    # CSS for animations
    st.markdown("""
    <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        
        .voice-active {
            animation: pulse 2s infinite;
            border: 2px solid #00b894;
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Start the continuous conversation
    st.session_state.voice_agent.start_continuous_conversation()
    
    # Handle any pending voice responses
    if st.session_state.get('should_play_response'):
        if st.session_state.get('last_ai_response'):
            st.session_state.voice_agent._play_immediate_response(st.session_state.last_ai_response)
        st.session_state.should_play_response = False