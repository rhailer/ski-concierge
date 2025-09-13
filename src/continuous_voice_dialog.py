import streamlit as st
import tempfile
import os
import time
import threading
from typing import Optional, Callable
import base64
from config.settings import Config

class ContinuousVoiceDialog:
    def __init__(self, openai_client, on_voice_message: Callable[[str], None]):
        self.client = openai_client
        self.on_voice_message = on_voice_message
        self.is_listening = False
        self.current_audio_file = None
        
    def render_voice_interface(self):
        """Render continuous voice dialog interface"""
        
        # Voice conversation header
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
                   padding: 2rem; border-radius: 20px; text-align: center; margin: 2rem 0;'>
            <h2 style='margin: 0 0 1rem 0;'>🎤 Voice Conversation Mode</h2>
            <p style='margin: 0; font-size: 1.1rem; opacity: 0.9;'>
                Have a natural voice conversation about your ski needs
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Voice recording section
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Recording instructions
            if not st.session_state.get('voice_conversation_started', False):
                st.markdown("""
                <div style='background: #e8f5e8; padding: 1.5rem; border-radius: 15px; 
                           border-left: 4px solid #4caf50; margin: 1rem 0;'>
                    <h4 style='color: #2e7d32; margin-top: 0;'>🎯 How Voice Dialog Works:</h4>
                    <ol style='color: #388e3c; line-height: 1.6;'>
                        <li><strong>Record:</strong> Use the recorder below to speak your message</li>
                        <li><strong>Send:</strong> Your voice will be transcribed automatically</li>
                        <li><strong>Listen:</strong> I'll respond with both text and voice</li>
                        <li><strong>Continue:</strong> Keep the conversation going naturally!</li>
                    </ol>
                </div>
                """, unsafe_allow_html=True)
            
            # Voice recorder
            self._render_voice_recorder()
            
            # Alternative: File upload for mobile users
            st.markdown("---")
            st.markdown("### 📱 Or upload a voice message:")
            
            uploaded_audio = st.file_uploader(
                "Record on your phone and upload here",
                type=['mp3', 'wav', 'm4a', 'ogg', 'webm'],
                key="voice_upload",
                help="Record a voice message on your device and upload it"
            )
            
            if uploaded_audio:
                st.audio(uploaded_audio, format='audio/wav')
                
                if st.button("🎧 Process Voice Message", type="primary", key="process_upload"):
                    with st.spinner("🎧 Understanding your message..."):
                        transcription = self._transcribe_uploaded_file(uploaded_audio)
                        if transcription:
                            st.success(f"✅ You said: *\"{transcription}\"*")
                            self._handle_voice_input(transcription)
                            return True
            
            # Quick voice prompts
            st.markdown("---")
            st.markdown("### 💡 Try these voice prompts:")
            
            voice_examples = [
                "I'm looking for intermediate all-mountain skis",
                "What's the difference between these ski recommendations?",
                "Help me choose the right ski length for my height",
                "I need skis for powder skiing in Colorado"
            ]
            
            for i, example in enumerate(voice_examples):
                if st.button(f"🗣️ \"{example}\"", key=f"voice_example_{i}"):
                    self._handle_voice_input(example)
                    return True
        
        return False
    
    def _render_voice_recorder(self):
        """Render the voice recording interface"""
        
        # Custom HTML for voice recording (fallback approach)
        st.markdown("""
        <div style='text-align: center; margin: 2rem 0;'>
            <div id='voice-recorder-container' style='background: white; padding: 2rem; 
                                                     border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);'>
                <div id='recording-status' style='margin-bottom: 1rem; font-weight: 600; color: #666;'>
                    Ready to record your voice message
                </div>
                
                <button id='record-btn' onclick='toggleRecording()' 
                        style='background: linear-gradient(135deg, #e74c3c, #c0392b); 
                               color: white; border: none; border-radius: 50px; 
                               padding: 1rem 2rem; font-size: 1.1rem; font-weight: 600; 
                               cursor: pointer; transition: all 0.3s ease;'>
                    🎤 Start Recording
                </button>
                
                <div id='recording-animation' style='display: none; margin: 1rem 0;'>
                    <div style='width: 100px; height: 100px; margin: 0 auto; 
                               background: #e74c3c; border-radius: 50%; 
                               animation: pulse 1.5s ease-in-out infinite;'></div>
                </div>
                
                <audio id='audio-playback' controls style='margin: 1rem 0; display: none; width: 100%;'></audio>
                
                <button id='send-btn' onclick='sendRecording()' 
                        style='background: linear-gradient(135deg, #27ae60, #229954); 
                               color: white; border: none; border-radius: 50px; 
                               padding: 1rem 2rem; font-size: 1.1rem; font-weight: 600; 
                               cursor: pointer; margin: 1rem; display: none;'>
                    📤 Send Voice Message
                </button>
            </div>
        </div>
        
        <style>
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.1); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
        }
        
        #record-btn:hover, #send-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        }
        </style>
        
        <script>
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        
        async function toggleRecording() {
            const recordBtn = document.getElementById('record-btn');
            const statusDiv = document.getElementById('recording-status');
            const animationDiv = document.getElementById('recording-animation');
            const audioPlayback = document.getElementById('audio-playback');
            const sendBtn = document.getElementById('send-btn');
            
            if (!isRecording) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = event => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const audioUrl = URL.createObjectURL(audioBlob);
                        audioPlayback.src = audioUrl;
                        audioPlayback.style.display = 'block';
                        sendBtn.style.display = 'inline-block';
                        
                        // Store for sending
                        window.recordedAudioBlob = audioBlob;
                    };
                    
                    mediaRecorder.start();
                    isRecording = true;
                    
                    recordBtn.textContent = '⏹️ Stop Recording';
                    recordBtn.style.background = 'linear-gradient(135deg, #c0392b, #a93226)';
                    statusDiv.textContent = '🔴 Recording... Click stop when finished';
                    statusDiv.style.color = '#e74c3c';
                    animationDiv.style.display = 'block';
                    
                } catch (err) {
                    console.error('Error accessing microphone:', err);
                    statusDiv.textContent = '❌ Microphone access denied. Please use file upload instead.';
                    statusDiv.style.color = '#e74c3c';
                }
            } else {
                mediaRecorder.stop();
                isRecording = false;
                
                recordBtn.textContent = '🎤 Start Recording';
                recordBtn.style.background = 'linear-gradient(135deg, #e74c3c, #c0392b)';
                statusDiv.textContent = '✅ Recording complete! Listen and send below';
                statusDiv.style.color = '#27ae60';
                animationDiv.style.display = 'none';
                
                // Stop all tracks
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
        }
        
        function sendRecording() {
            if (window.recordedAudioBlob) {
                // Convert to base64 and trigger Streamlit processing
                const reader = new FileReader();
                reader.onload = function(event) {
                    const base64Audio = event.target.result.split(',')[1];
                    
                    // Store in session state for Streamlit to process
                    window.parent.postMessage({
                        type: 'VOICE_RECORDING',
                        audio: base64Audio,
                        mimeType: 'audio/wav'
                    }, '*');
                };
                reader.readAsDataURL(window.recordedAudioBlob);
                
                document.getElementById('recording-status').textContent = '📤 Processing your message...';
                document.getElementById('send-btn').style.display = 'none';
            }
        }
        </script>
        """, unsafe_allow_html=True)
        
        # Check for recorded audio from JavaScript
        if 'voice_recording_data' in st.session_state:
            audio_data = st.session_state.voice_recording_data
            del st.session_state.voice_recording_data
            
            with st.spinner("🎧 Transcribing your voice..."):
                transcription = self._transcribe_base64_audio(audio_data)
                if transcription:
                    st.success(f"✅ You said: *\"{transcription}\"*")
                    self._handle_voice_input(transcription)
                    return True
    
    def _transcribe_uploaded_file(self, uploaded_file) -> Optional[str]:
        """Transcribe uploaded audio file"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            with open(tmp_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=Config.VOICE_MODEL,
                    file=audio_file,
                    response_format="text"
                )
            
            os.unlink(tmp_file_path)
            return transcript.strip() if transcript.strip() else None
            
        except Exception as e:
            st.error(f"Error transcribing audio: {e}")
            return None
    
    def _transcribe_base64_audio(self, base64_audio: str) -> Optional[str]:
        """Transcribe base64 encoded audio"""
        try:
            import base64
            audio_data = base64.b64decode(base64_audio)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_data)
                tmp_file_path = tmp_file.name
            
            with open(tmp_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=Config.VOICE_MODEL,
                    file=audio_file,
                    response_format="text"
                )
            
            os.unlink(tmp_file_path)
            return transcript.strip() if transcript.strip() else None
            
        except Exception as e:
            st.error(f"Error transcribing audio: {e}")
            return None
    
    def _handle_voice_input(self, transcription: str):
        """Handle voice input and trigger conversation"""
        if transcription:
            st.session_state.voice_conversation_started = True
            self.on_voice_message(transcription)
    
    def create_voice_response(self, text: str) -> Optional[bytes]:
        """Create voice response using TTS"""
        try:
            response = self.client.audio.speech.create(
                model=Config.TTS_MODEL,
                voice=Config.TTS_VOICE,
                input=text,
                response_format="mp3"
            )
            return response.content
        except Exception as e:
            st.warning(f"Voice response not available: {e}")
            return None
    
    def play_voice_response(self, text: str):
        """Play voice response"""
        st.markdown("### 🔊 My Voice Response:")
        
        with st.spinner("🎵 Generating voice response..."):
            audio_bytes = self.create_voice_response(text)
        
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            st.success("🎧 Voice response ready! (Playing automatically)")
            
            # Encourage continuation
            st.markdown("""
            <div style='background: #e8f5e8; padding: 1rem; border-radius: 10px; 
                       text-align: center; margin: 1rem 0; border-left: 4px solid #4caf50;'>
                <strong>💬 Keep the conversation going!</strong><br>
                Record another message or ask follow-up questions
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("📝 Voice response not available, but you have my text response above!")

def handle_voice_message(transcription: str):
    """Handle voice message in the conversation"""
    st.session_state.voice_input_received = transcription
    st.session_state.process_voice_input = True