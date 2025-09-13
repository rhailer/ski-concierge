import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os
import json
import base64
from typing import Callable
from config.settings import Config

class RealContinuousVoice:
    def __init__(self, openai_client, on_voice_callback: Callable[[str], str]):
        self.client = openai_client
        self.on_voice_callback = on_voice_callback
        
    def render_continuous_voice_dialog(self):
        """Render true continuous voice dialog interface"""
        
        # Voice conversation header
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
                   padding: 2rem; border-radius: 20px; text-align: center; margin: 2rem 0;'>
            <h2 style='margin: 0 0 1rem 0;'>🎤 Continuous Voice Dialog</h2>
            <p style='margin: 0; font-size: 1.2rem; opacity: 0.9;'>
                Talk naturally - I'll listen and respond in real-time!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # JavaScript-based continuous voice interface
        voice_html = self._create_voice_interface_html()
        
        # Render the voice interface
        voice_data = components.html(voice_html, height=600, scrolling=False)
        
        # Handle voice input if received
        self._handle_voice_data()
        
        # Show conversation status
        self._show_conversation_status()
    
    def _create_voice_interface_html(self):
        """Create the HTML/JS for continuous voice interface"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
                }}
                
                .voice-container {{
                    background: white;
                    border-radius: 25px;
                    padding: 2rem;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                    text-align: center;
                    max-width: 600px;
                    margin: 0 auto;
                }}
                
                .status-display {{
                    font-size: 1.2rem;
                    font-weight: 600;
                    margin: 1rem 0;
                    color: #333;
                    min-height: 60px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: #f8f9fa;
                    border-radius: 15px;
                    padding: 1rem;
                }}
                
                .voice-button {{
                    background: linear-gradient(135deg, #e74c3c, #c0392b);
                    color: white;
                    border: none;
                    border-radius: 50px;
                    padding: 1.5rem 3rem;
                    font-size: 1.3rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    margin: 1rem;
                    box-shadow: 0 6px 25px rgba(231, 76, 60, 0.3);
                }}
                
                .voice-button:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 10px 35px rgba(231, 76, 60, 0.4);
                }}
                
                .voice-button.listening {{
                    background: linear-gradient(135deg, #27ae60, #229954);
                    animation: pulse 2s infinite;
                }}
                
                .voice-button.processing {{
                    background: linear-gradient(135deg, #3498db, #2980b9);
                    cursor: not-allowed;
                }}
                
                @keyframes pulse {{
                    0% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.05); }}
                    100% {{ transform: scale(1); }}
                }}
                
                .conversation-display {{
                    text-align: left;
                    margin: 2rem 0;
                    max-height: 300px;
                    overflow-y: auto;
                    background: #f8f9fa;
                    border-radius: 15px;
                    padding: 1rem;
                }}
                
                .message {{
                    margin: 1rem 0;
                    padding: 1rem;
                    border-radius: 15px;
                    animation: fadeIn 0.5s ease-in;
                }}
                
                .user-message {{
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    margin-left: 20%;
                }}
                
                .ai-message {{
                    background: linear-gradient(135deg, #f1f2f6, #ddd);
                    color: #333;
                    margin-right: 20%;
                }}
                
                @keyframes fadeIn {{
                    from {{ opacity: 0; transform: translateY(10px); }}
                    to {{ opacity: 1; transform: translateY(0); }}
                }}
                
                .quick-responses {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1rem;
                    margin: 2rem 0;
                }}
                
                .quick-btn {{
                    background: #e3f2fd;
                    border: 2px solid #1976d2;
                    border-radius: 20px;
                    padding: 0.8rem;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    font-weight: 500;
                    color: #1976d2;
                }}
                
                .quick-btn:hover {{
                    background: #1976d2;
                    color: white;
                    transform: translateY(-2px);
                }}
            </style>
        </head>
        <body>
            <div class="voice-container">
                <div id="status" class="status-display">
                    🎤 Click "Start Conversation" to begin talking
                </div>
                
                <button id="voiceButton" class="voice-button" onclick="toggleVoiceConversation()">
                    🎤 Start Conversation
                </button>
                
                <div id="conversation" class="conversation-display" style="display: none;">
                    <!-- Conversation will appear here -->
                </div>
                
                <div class="quick-responses">
                    <button class="quick-btn" onclick="simulateVoice('I need help finding skis for intermediate skiing')">
                        🗣️ "I need intermediate skis"
                    </button>
                    <button class="quick-btn" onclick="simulateVoice('What is the difference between these options?')">
                        🗣️ "Compare these options"
                    </button>
                    <button class="quick-btn" onclick="simulateVoice('I ski powder in Colorado')">
                        🗣️ "I ski powder"
                    </button>
                    <button class="quick-btn" onclick="simulateVoice('Help me choose the right size')">
                        🗣️ "Help with sizing"
                    </button>
                </div>
            </div>
            
            <script>
                let isListening = false;
                let mediaRecorder = null;
                let audioChunks = [];
                let conversationActive = false;
                let speechRecognition = null;
                
                // Initialize speech recognition if available
                if ('webkitSpeechRecognition' in window) {{
                    speechRecognition = new webkitSpeechRecognition();
                    speechRecognition.continuous = true;
                    speechRecognition.interimResults = true;
                    speechRecognition.lang = 'en-US';
                    
                    speechRecognition.onresult = function(event) {{
                        let finalTranscript = '';
                        for (let i = event.resultIndex; i < event.results.length; i++) {{
                            if (event.results[i].isFinal) {{
                                finalTranscript += event.results[i][0].transcript;
                            }}
                        }}
                        
                        if (finalTranscript.trim().length > 0) {{
                            processVoiceInput(finalTranscript.trim());
                        }}
                    }};
                    
                    speechRecognition.onerror = function(event) {{
                        console.log('Speech recognition error:', event.error);
                        updateStatus('❌ Speech recognition error. Trying microphone recording...');
                        startMicRecording();
                    }};
                }}
                
                function toggleVoiceConversation() {{
                    const button = document.getElementById('voiceButton');
                    
                    if (!isListening) {{
                        startListening();
                    }} else {{
                        stopListening();
                    }}
                }}
                
                function startListening() {{
                    isListening = true;
                    conversationActive = true;
                    
                    const button = document.getElementById('voiceButton');
                    button.textContent = '⏸️ Stop Conversation';
                    button.classList.add('listening');
                    
                    updateStatus('🎤 Listening... Start talking naturally!');
                    
                    document.getElementById('conversation').style.display = 'block';
                    
                    // Try speech recognition first
                    if (speechRecognition) {{
                        try {{
                            speechRecognition.start();
                        }} catch (e) {{
                            console.log('Speech recognition failed, using microphone');
                            startMicRecording();
                        }}
                    }} else {{
                        startMicRecording();
                    }}
                }}
                
                function stopListening() {{
                    isListening = false;
                    
                    const button = document.getElementById('voiceButton');
                    button.textContent = '🎤 Start Conversation';
                    button.classList.remove('listening');
                    
                    updateStatus('👋 Conversation paused. Click to resume anytime!');
                    
                    if (speechRecognition) {{
                        speechRecognition.stop();
                    }}
                    
                    if (mediaRecorder && mediaRecorder.state === 'recording') {{
                        mediaRecorder.stop();
                    }}
                }}
                
                function startMicRecording() {{
                    navigator.mediaDevices.getUserMedia({{ audio: true }})
                        .then(stream => {{
                            mediaRecorder = new MediaRecorder(stream);
                            audioChunks = [];
                            
                            mediaRecorder.ondataavailable = event => {{
                                audioChunks.push(event.data);
                            }};
                            
                            mediaRecorder.onstop = () => {{
                                const audioBlob = new Blob(audioChunks, {{ type: 'audio/wav' }});
                                sendAudioForTranscription(audioBlob);
                            }};
                            
                            mediaRecorder.start();
                            setTimeout(() => {{
                                if (mediaRecorder && mediaRecorder.state === 'recording') {{
                                    mediaRecorder.stop();
                                    if (isListening) {{
                                        setTimeout(startMicRecording, 100); // Restart recording
                                    }}
                                }}
                            }}, 3000); // Record in 3-second chunks
                        }})
                        .catch(err => {{
                            updateStatus('❌ Microphone access denied. Please use quick responses below.');
                        }});
                }}
                
                function sendAudioForTranscription(audioBlob) {{
                    const reader = new FileReader();
                    reader.onload = function(event) {{
                        const base64Audio = event.target.result.split(',')[1];
                        
                        // Send to parent Streamlit app
                        window.parent.postMessage({{
                            type: 'VOICE_TRANSCRIPTION_REQUEST',
                            audioData: base64Audio,
                            timestamp: Date.now()
                        }}, '*');
                    }};
                    reader.readAsDataURL(audioBlob);
                }}
                
                function processVoiceInput(transcript) {{
                    if (!transcript || transcript.length < 2) return;
                    
                    updateStatus('🧠 Processing: "' + transcript + '"');
                    
                    // Add user message to conversation
                    addMessageToConversation('user', transcript);
                    
                    // Send to Streamlit for AI response
                    window.parent.postMessage({{
                        type: 'VOICE_INPUT',
                        transcript: transcript,
                        timestamp: Date.now()
                    }}, '*');
                }}
                
                function simulateVoice(text) {{
                    processVoiceInput(text);
                }}
                
                function addMessageToConversation(sender, message) {{
                    const conversation = document.getElementById('conversation');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${{sender}}-message`;
                    
                    const prefix = sender === 'user' ? '🗣️ You: ' : '🎿 Ski Expert: ';
                    messageDiv.textContent = prefix + message;
                    
                    conversation.appendChild(messageDiv);
                    conversation.scrollTop = conversation.scrollHeight;
                }}
                
                function updateStatus(message) {{
                    document.getElementById('status').textContent = message;
                }}
                
                // Listen for responses from Streamlit
                window.addEventListener('message', function(event) {{
                    if (event.data.type === 'AI_RESPONSE') {{
                        addMessageToConversation('ai', event.data.response);
                        updateStatus('🎤 Keep talking! I\\'m listening for your next question...');
                    }} else if (event.data.type === 'TRANSCRIPTION_RESULT') {{
                        if (event.data.transcript) {{
                            processVoiceInput(event.data.transcript);
                        }}
                    }}
                }});
            </script>
        </body>
        </html>
        """
    
    def _handle_voice_data(self):
        """Handle voice data from JavaScript"""
        # Check for voice input
        if st.session_state.get('voice_input_received'):
            transcript = st.session_state.voice_input_received
            del st.session_state.voice_input_received
            
            # Process with AI
            ai_response = self.on_voice_callback(transcript)
            
            # Play TTS response
            self._play_tts_response(ai_response)
            
            # Send response back to JavaScript
            st.session_state.ai_response_ready = ai_response
        
        # Check for transcription request
        if st.session_state.get('transcription_request'):
            audio_data = st.session_state.transcription_request
            del st.session_state.transcription_request
            
            # Transcribe audio
            transcript = self._transcribe_base64_audio(audio_data)
            st.session_state.transcription_result = transcript
    
    def _transcribe_base64_audio(self, base64_audio: str) -> str:
        """Transcribe base64 audio data"""
        try:
            audio_bytes = base64.b64decode(base64_audio)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name
            
            with open(tmp_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=Config.VOICE_MODEL,
                    file=audio_file,
                    response_format="text"
                )
            
            os.unlink(tmp_file_path)
            return transcript.strip() if transcript else ""
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    def _play_tts_response(self, text: str):
        """Play TTS response"""
        try:
            response = self.client.audio.speech.create(
                model=Config.TTS_MODEL,
                voice=Config.TTS_VOICE,
                input=text[:1500],
                response_format="mp3"
            )
            
            # Auto-play response
            st.audio(response.content, format="audio/mp3", autoplay=True)
            
        except Exception as e:
            print(f"TTS error: {e}")
    
    def _show_conversation_status(self):
        """Show conversation status and tips"""
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 Conversation Tips
            - **Start naturally**: "I need help finding skis"
            - **Ask follow-ups**: "What's the difference?"
            - **Be specific**: "I ski powder in Colorado"
            - **Get details**: "Help me choose the right size"
            """)
        
        with col2:
            st.markdown("""
            ### 🔧 Technical Status
            - ✅ **Speech Recognition**: Browser-based
            - ✅ **Microphone Recording**: Fallback mode  
            - ✅ **AI Processing**: OpenAI GPT-4
            - ✅ **Voice Response**: OpenAI TTS
            """)

# JavaScript message handler
js_handler = """
<script>
window.addEventListener('message', function(event) {
    if (event.data.type === 'VOICE_INPUT') {
        // Store transcript for Streamlit
        window.streamlitVoiceInput = event.data.transcript;
    } else if (event.data.type === 'VOICE_TRANSCRIPTION_REQUEST') {
        // Store audio data for transcription
        window.streamlitTranscriptionRequest = event.data.audioData;
    }
});

// Polling function to check for data
setInterval(function() {
    if (window.streamlitVoiceInput) {
        window.parent.postMessage({
            type: 'STREAMLIT_VOICE_DATA',
            data: window.streamlitVoiceInput
        }, '*');
        window.streamlitVoiceInput = null;
    }
    
    if (window.streamlitTranscriptionRequest) {
        window.parent.postMessage({
            type: 'STREAMLIT_TRANSCRIPTION_DATA', 
            data: window.streamlitTranscriptionRequest
        }, '*');
        window.streamlitTranscriptionRequest = null;
    }
}, 100);
</script>
"""

def render_js_handler():
    """Render JavaScript handler"""
    components.html(js_handler, height=0)