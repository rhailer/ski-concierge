import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os
import time
from typing import Optional, Callable
import base64
from config.settings import Config

class WorkingVoiceInterface:
    def __init__(self, openai_client, on_voice_message: Callable[[str], None]):
        self.client = openai_client
        self.on_voice_message = on_voice_message
        
    def render_voice_interface(self):
        """Render working voice interface using Streamlit components"""
        
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
        
        # Method 1: Working HTML5 Voice Recorder Component
        st.markdown("### 🎤 Voice Recorder")
        
        # Custom HTML component that actually works
        voice_recorder_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .voice-container {
                    background: white;
                    padding: 2rem;
                    border-radius: 20px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                    text-align: center;
                    margin: 1rem 0;
                }
                
                .record-button {
                    background: linear-gradient(135deg, #e74c3c, #c0392b);
                    color: white;
                    border: none;
                    border-radius: 50px;
                    padding: 1rem 2rem;
                    font-size: 1.1rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    margin: 1rem;
                }
                
                .record-button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(231, 76, 60, 0.3);
                }
                
                .record-button.recording {
                    background: linear-gradient(135deg, #c0392b, #a93226);
                    animation: pulse 1.5s ease-in-out infinite;
                }
                
                .send-button {
                    background: linear-gradient(135deg, #27ae60, #229954);
                    color: white;
                    border: none;
                    border-radius: 50px;
                    padding: 1rem 2rem;
                    font-size: 1.1rem;
                    font-weight: 600;
                    cursor: pointer;
                    margin: 1rem;
                    display: none;
                }
                
                .send-button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(39, 174, 96, 0.3);
                }
                
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }
                
                .status {
                    margin: 1rem 0;
                    font-weight: 600;
                    color: #666;
                }
                
                .recording-indicator {
                    display: none;
                    margin: 1rem 0;
                }
                
                .recording-dot {
                    width: 20px;
                    height: 20px;
                    background: #e74c3c;
                    border-radius: 50%;
                    display: inline-block;
                    animation: blink 1s ease-in-out infinite;
                    margin-right: 0.5rem;
                }
                
                @keyframes blink {
                    0%, 50% { opacity: 1; }
                    51%, 100% { opacity: 0.3; }
                }
                
                audio {
                    width: 100%;
                    margin: 1rem 0;
                    display: none;
                }
            </style>
        </head>
        <body>
            <div class="voice-container">
                <div id="status" class="status">Ready to record your voice message</div>
                
                <button id="recordButton" class="record-button" onclick="toggleRecording()">
                    🎤 Start Recording
                </button>
                
                <div id="recordingIndicator" class="recording-indicator">
                    <span class="recording-dot"></span>Recording... Click stop when finished
                </div>
                
                <audio id="audioPlayback" controls></audio>
                
                <button id="sendButton" class="send-button" onclick="sendRecording()">
                    📤 Send Voice Message
                </button>
                
                <div id="transcript" style="margin-top: 1rem; display: none;"></div>
            </div>
            
            <script>
                let mediaRecorder;
                let audioChunks = [];
                let isRecording = false;
                let audioBlob = null;
                
                async function toggleRecording() {
                    const recordButton = document.getElementById('recordButton');
                    const status = document.getElementById('status');
                    const recordingIndicator = document.getElementById('recordingIndicator');
                    const audioPlayback = document.getElementById('audioPlayback');
                    const sendButton = document.getElementById('sendButton');
                    
                    if (!isRecording) {
                        try {
                            const stream = await navigator.mediaDevices.getUserMedia({ 
                                audio: {
                                    echoCancellation: true,
                                    noiseSuppression: true,
                                    autoGainControl: true
                                }
                            });
                            
                            mediaRecorder = new MediaRecorder(stream, {
                                mimeType: 'audio/webm;codecs=opus'
                            });
                            
                            audioChunks = [];
                            
                            mediaRecorder.ondataavailable = event => {
                                if (event.data.size > 0) {
                                    audioChunks.push(event.data);
                                }
                            };
                            
                            mediaRecorder.onstop = async () => {
                                audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                                const audioUrl = URL.createObjectURL(audioBlob);
                                audioPlayback.src = audioUrl;
                                audioPlayback.style.display = 'block';
                                sendButton.style.display = 'inline-block';
                                
                                status.textContent = '✅ Recording complete! Listen and send below';
                                status.style.color = '#27ae60';
                            };
                            
                            mediaRecorder.start(1000);
                            isRecording = true;
                            
                            recordButton.textContent = '⏹️ Stop Recording';
                            recordButton.classList.add('recording');
                            status.textContent = '🔴 Recording in progress...';
                            status.style.color = '#e74c3c';
                            recordingIndicator.style.display = 'block';
                            
                        } catch (err) {
                            console.error('Error accessing microphone:', err);
                            status.textContent = '❌ Microphone access denied. Please use file upload below.';
                            status.style.color = '#e74c3c';
                        }
                    } else {
                        if (mediaRecorder && mediaRecorder.state === 'recording') {
                            mediaRecorder.stop();
                            mediaRecorder.stream.getTracks().forEach(track => track.stop());
                        }
                        
                        isRecording = false;
                        recordButton.textContent = '🎤 Start Recording';
                        recordButton.classList.remove('recording');
                        recordingIndicator.style.display = 'none';
                    }
                }
                
                async function sendRecording() {
                    if (!audioBlob) return;
                    
                    const status = document.getElementById('status');
                    const sendButton = document.getElementById('sendButton');
                    
                    status.textContent = '📤 Processing your voice message...';
                    status.style.color = '#3498db';
                    sendButton.style.display = 'none';
                    
                    try {
                        // Convert blob to base64
                        const reader = new FileReader();
                        reader.onload = function(event) {
                            const base64Audio = event.target.result;
                            
                            // Send to parent (Streamlit)
                            window.parent.postMessage({
                                type: 'VOICE_RECORDING_READY',
                                audioData: base64Audio,
                                timestamp: Date.now()
                            }, '*');
                            
                            status.textContent = '✨ Voice message sent! Processing...';
                            status.style.color = '#27ae60';
                        };
                        reader.readAsDataURL(audioBlob);
                        
                    } catch (error) {
                        console.error('Error sending recording:', error);
                        status.textContent = '❌ Error sending recording. Please try again.';
                        status.style.color = '#e74c3c';
                        sendButton.style.display = 'inline-block';
                    }
                }
                
                // Reset function for new recording
                function resetRecorder() {
                    const status = document.getElementById('status');
                    const recordButton = document.getElementById('recordButton');
                    const audioPlayback = document.getElementById('audioPlayback');
                    const sendButton = document.getElementById('sendButton');
                    const recordingIndicator = document.getElementById('recordingIndicator');
                    
                    audioBlob = null;
                    audioChunks = [];
                    isRecording = false;
                    
                    status.textContent = 'Ready for your next message';
                    status.style.color = '#666';
                    recordButton.textContent = '🎤 Start Recording';
                    recordButton.classList.remove('recording');
                    audioPlayback.style.display = 'none';
                    sendButton.style.display = 'none';
                    recordingIndicator.style.display = 'none';
                }
                
                // Listen for reset message from parent
                window.addEventListener('message', function(event) {
                    if (event.data.type === 'RESET_VOICE_RECORDER') {
                        resetRecorder();
                    }
                });
            </script>
        </body>
        </html>
        """
        
        # Render the working HTML component
        voice_response = components.html(voice_recorder_html, height=400, scrolling=False)
        
        # Check for voice recording data from the component
        if st.session_state.get('voice_recording_received'):
            audio_data = st.session_state.voice_recording_received
            del st.session_state.voice_recording_received
            
            with st.spinner("🎧 Transcribing your voice..."):
                transcription = self._process_voice_data(audio_data)
                if transcription:
                    st.success(f"✅ You said: *\"{transcription}\"*")
                    self.on_voice_message(transcription)
                    return True
        
        # Method 2: File Upload Alternative
        st.markdown("---")
        st.markdown("### 📱 Alternative: Upload Voice Message")
        st.info("💡 If the recorder above doesn't work, record on your phone/computer and upload here!")
        
        uploaded_audio = st.file_uploader(
            "Choose an audio file",
            type=['mp3', 'wav', 'm4a', 'ogg', 'webm', 'mp4'],
            key="voice_file_upload",
            help="Record a voice message and upload it here"
        )
        
        if uploaded_audio:
            st.audio(uploaded_audio, format='audio/wav')
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🎧 Process Uploaded Voice", type="primary", use_container_width=True):
                    with st.spinner("🎧 Transcribing your uploaded message..."):
                        transcription = self._transcribe_uploaded_file(uploaded_audio)
                        if transcription:
                            st.success(f"✅ You said: *\"{transcription}\"*")
                            self.on_voice_message(transcription)
                            return True
        
        # Method 3: Quick Voice Examples
        st.markdown("---")
        st.markdown("### 💡 Try These Voice Examples")
        st.info("Click any button below to simulate voice input and see how the conversation works!")
        
        voice_examples = [
            "I'm an intermediate skier looking for all-mountain skis under 600 dollars",
            "I ski powder in Colorado about 20 days a year, what do you recommend?",
            "What's the difference between carving skis and all-mountain skis?",
            "I'm 5 foot 8 inches and weigh 165 pounds, what ski length should I get?",
            "Compare these ski recommendations and help me choose the best one",
            "Show me some alternatives in a different price range"
        ]
        
        example_cols = st.columns(2)
        for i, example in enumerate(voice_examples):
            col = example_cols[i % 2]
            with col:
                if st.button(f"🗣️ \"{example[:30]}...\"", key=f"voice_example_{i}", help=example):
                    st.success(f"✅ Voice simulation: *\"{example}\"*")
                    self.on_voice_message(example)
                    return True
        
        return False
    
    def _process_voice_data(self, audio_data: str) -> Optional[str]:
        """Process voice data from the HTML component"""
        try:
            # Extract base64 data
            if 'base64,' in audio_data:
                audio_base64 = audio_data.split('base64,')[1]
            else:
                audio_base64 = audio_data
            
            # Decode and save temporarily
            audio_bytes = base64.b64decode(audio_base64)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
                tmp_file.write(audio_bytes)
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
            st.error(f"Error processing voice: {e}")
            return None
    
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
            st.error(f"Error transcribing uploaded file: {e}")
            return None
    
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
        """Play voice response with enhanced UI"""
        st.markdown("""
        <div style='background: linear-gradient(135deg, #e8f5e8, #f3e5f5); 
                   padding: 2rem; border-radius: 20px; margin: 2rem 0; 
                   border-left: 4px solid #4caf50;'>
            <h3 style='color: #2e7d32; margin: 0 0 1rem 0;'>🔊 My Voice Response:</h3>
        """, unsafe_allow_html=True)
        
        with st.spinner("🎵 Generating voice response..."):
            audio_bytes = self.create_voice_response(text)
        
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            st.success("🎧 Voice response ready! (Playing automatically)")
            
            # Encourage continuation
            st.markdown("""
            <div style='background: rgba(76, 175, 80, 0.1); padding: 1rem; border-radius: 10px; 
                       text-align: center; margin: 1rem 0;'>
                <strong>💬 Keep the conversation going!</strong><br>
                Record another message or ask follow-up questions about the skis!
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("📝 Voice response not available, but you have my text response above!")
        
        st.markdown("</div>", unsafe_allow_html=True)

# JavaScript message handler for voice recording
def handle_voice_message_js():
    """Handle JavaScript messages from voice recorder"""
    js_code = """
    <script>
        window.addEventListener('message', function(event) {
            if (event.data.type === 'VOICE_RECORDING_READY') {
                // Store the audio data in Streamlit session state
                window.parent.postMessage({
                    type: 'STREAMLIT_SET_STATE',
                    key: 'voice_recording_received',
                    value: event.data.audioData
                }, '*');
                
                // Trigger a rerun
                window.parent.postMessage({
                    type: 'STREAMLIT_RERUN'
                }, '*');
            }
        });
    </script>
    """
    components.html(js_code, height=0)