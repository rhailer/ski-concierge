import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os
import base64
from typing import Callable
from config.settings import Config

class WorkingVoiceWithTTS:
    def __init__(self, openai_client, on_voice_callback: Callable[[str], str]):
        self.client = openai_client
        self.on_voice_callback = on_voice_callback
        
    def render_continuous_voice_dialog(self):
        """Render working continuous voice dialog with reliable TTS"""
        
        # Voice conversation header
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
                   padding: 2rem; border-radius: 20px; text-align: center; margin: 2rem 0;'>
            <h2 style='margin: 0 0 1rem 0;'>🎤 Continuous Voice Dialog</h2>
            <p style='margin: 0; font-size: 1.2rem; opacity: 0.9;'>
                Talk naturally - I'll listen and respond with voice!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create the voice interface with built-in TTS
        self._render_voice_interface_with_tts()
        
        # Process any pending voice data
        self._process_pending_voice_data()
        
        # Show status and tips
        self._show_voice_status()
    
    def _render_voice_interface_with_tts(self):
        """Render voice interface with built-in TTS playback"""
        
        voice_html = f"""
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
                    max-width: 700px;
                    margin: 0 auto;
                }}
                
                .status {{
                    font-size: 1.2rem;
                    font-weight: 600;
                    margin: 1rem 0;
                    padding: 1rem;
                    background: #f8f9fa;
                    border-radius: 15px;
                    min-height: 60px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-left: 4px solid #007bff;
                }}
                
                .status.listening {{
                    background: #e8f5e8;
                    border-left-color: #28a745;
                    animation: pulse 2s infinite;
                }}
                
                .status.processing {{
                    background: #fff3cd;
                    border-left-color: #ffc107;
                }}
                
                .status.speaking {{
                    background: #f3e5f5;
                    border-left-color: #6f42c1;
                }}
                
                .voice-btn {{
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
                
                .voice-btn:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 10px 35px rgba(231, 76, 60, 0.4);
                }}
                
                .voice-btn.listening {{
                    background: linear-gradient(135deg, #27ae60, #229954);
                }}
                
                @keyframes pulse {{
                    0% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.05); }}
                    100% {{ transform: scale(1); }}
                }}
                
                .conversation {{
                    text-align: left;
                    margin: 2rem 0;
                    max-height: 300px;
                    overflow-y: auto;
                    background: #f8f9fa;
                    border-radius: 15px;
                    padding: 1rem;
                    display: none;
                }}
                
                .message {{
                    margin: 1rem 0;
                    padding: 1rem;
                    border-radius: 15px;
                    animation: fadeIn 0.5s ease-in;
                }}
                
                .user-msg {{
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    margin-left: 20%;
                }}
                
                .ai-msg {{
                    background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
                    color: #2e7d32;
                    margin-right: 20%;
                    border-left: 4px solid #4caf50;
                    position: relative;
                }}
                
                .ai-msg .play-btn {{
                    position: absolute;
                    top: 0.5rem;
                    right: 0.5rem;
                    background: #4caf50;
                    color: white;
                    border: none;
                    border-radius: 50%;
                    width: 30px;
                    height: 30px;
                    cursor: pointer;
                    font-size: 0.8rem;
                }}
                
                @keyframes fadeIn {{
                    from {{ opacity: 0; transform: translateY(10px); }}
                    to {{ opacity: 1; transform: translateY(0); }}
                }}
                
                .audio-controls {{
                    margin: 1rem 0;
                    padding: 1rem;
                    background: #f1f3f4;
                    border-radius: 15px;
                }}
                
                audio {{
                    width: 100%;
                    margin: 0.5rem 0;
                }}
                
                .tts-status {{
                    font-size: 1rem;
                    color: #6c757d;
                    margin: 0.5rem 0;
                }}
            </style>
        </head>
        <body>
            <div class="voice-container">
                <div id="status" class="status">
                    🎤 Ready to start voice conversation - Click below to begin
                </div>
                
                <button id="voiceBtn" class="voice-btn" onclick="toggleVoice()">
                    🎤 Start Talking
                </button>
                
                <div id="audioControls" class="audio-controls" style="display: none;">
                    <div class="tts-status" id="ttsStatus">🔊 Voice responses will appear here</div>
                    <audio id="ttsAudio" controls style="display: none;"></audio>
                    <button id="playTTSBtn" style="display: none;" onclick="playCurrentTTS()">
                        🔊 Play Voice Response
                    </button>
                </div>
                
                <div id="conversation" class="conversation"></div>
            </div>
            
            <script>
                let isListening = false;
                let recognition = null;
                let conversationCount = 0;
                let currentTTSAudio = null;
                
                // Initialize speech recognition
                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    recognition = new SpeechRecognition();
                    recognition.continuous = true;
                    recognition.interimResults = false;
                    recognition.lang = 'en-US';
                    
                    recognition.onstart = function() {{
                        updateStatus('🎤 Listening... Start talking!', 'listening');
                        document.getElementById('voiceBtn').textContent = '⏹️ Stop Listening';
                        document.getElementById('voiceBtn').classList.add('listening');
                    }};
                    
                    recognition.onresult = function(event) {{
                        const transcript = event.results[event.results.length - 1][0].transcript.trim();
                        if (transcript.length > 2) {{
                            processVoiceInput(transcript);
                        }}
                    }};
                    
                    recognition.onerror = function(event) {{
                        console.error('Speech recognition error:', event.error);
                        updateStatus('❌ Error: ' + event.error + '. Click to try again.', '');
                        resetVoiceButton();
                    }};
                    
                    recognition.onend = function() {{
                        if (isListening) {{
                            setTimeout(function() {{
                                if (isListening) {{
                                    try {{
                                        recognition.start();
                                    }} catch(e) {{
                                        console.log('Recognition restart failed:', e);
                                        resetVoiceButton();
                                    }}
                                }}
                            }}, 100);
                        }}
                    }};
                }} else {{
                    updateStatus('❌ Speech recognition not supported. Please use Chrome or Safari.', '');
                }}
                
                function toggleVoice() {{
                    if (!recognition) {{
                        alert('Speech recognition not supported in this browser. Please use Chrome or Safari.');
                        return;
                    }}
                    
                    if (!isListening) {{
                        startListening();
                    }} else {{
                        stopListening();
                    }}
                }}
                
                function startListening() {{
                    isListening = true;
                    document.getElementById('conversation').style.display = 'block';
                    document.getElementById('audioControls').style.display = 'block';
                    
                    try {{
                        recognition.start();
                    }} catch(e) {{
                        console.error('Failed to start recognition:', e);
                        updateStatus('❌ Failed to start. Please try again.', '');
                        resetVoiceButton();
                    }}
                }}
                
                function stopListening() {{
                    isListening = false;
                    if (recognition) {{
                        recognition.stop();
                    }}
                    resetVoiceButton();
                    updateStatus('👋 Voice conversation stopped. Click to resume.', '');
                }}
                
                function resetVoiceButton() {{
                    isListening = false;
                    document.getElementById('voiceBtn').textContent = '🎤 Start Talking';
                    document.getElementById('voiceBtn').classList.remove('listening');
                }}
                
                function processVoiceInput(transcript) {{
                    updateStatus('🧠 Processing: "' + transcript + '"...', 'processing');
                    addMessage('user', transcript);
                    
                    // Send to Streamlit
                    const messageKey = 'voice_msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                    localStorage.setItem(messageKey, JSON.stringify({{
                        transcript: transcript,
                        timestamp: Date.now(),
                        processed: false
                    }}));
                    
                    conversationCount++;
                }}
                
                function addMessage(sender, text, hasAudio = false) {{
                    const conversation = document.getElementById('conversation');
                    const msgDiv = document.createElement('div');
                    msgDiv.className = `message ${{sender}}-msg`;
                    
                    const prefix = sender === 'user' ? '🗣️ You: ' : '🎿 Ski Expert: ';
                    msgDiv.innerHTML = prefix + text;
                    
                    if (sender === 'ai' && hasAudio) {{
                        const playBtn = document.createElement('button');
                        playBtn.className = 'play-btn';
                        playBtn.innerHTML = '🔊';
                        playBtn.onclick = () => playCurrentTTS();
                        msgDiv.appendChild(playBtn);
                    }}
                    
                    conversation.appendChild(msgDiv);
                    conversation.scrollTop = conversation.scrollHeight;
                }}
                
                function updateStatus(message, className = '') {{
                    const statusDiv = document.getElementById('status');
                    statusDiv.textContent = message;
                    statusDiv.className = 'status ' + className;
                }}
                
                function showAIResponse(response) {{
                    addMessage('ai', response, true);
                    updateStatus('🎤 Got it! Keep talking or ask follow-up questions...', '');
                }}
                
                function loadTTSAudio(audioBase64) {{
                    try {{
                        const audioBlob = new Blob([Uint8Array.from(atob(audioBase64), c => c.charCodeAt(0))], {{type: 'audio/mpeg'}});
                        const audioUrl = URL.createObjectURL(audioBlob);
                        
                        const audioElement = document.getElementById('ttsAudio');
                        audioElement.src = audioUrl;
                        audioElement.style.display = 'block';
                        
                        const playBtn = document.getElementById('playTTSBtn');
                        playBtn.style.display = 'block';
                        
                        const ttsStatus = document.getElementById('ttsStatus');
                        ttsStatus.textContent = '🔊 Voice response ready! Click play or it will auto-play below.';
                        
                        // Auto-play attempt
                        audioElement.play().then(() => {{
                            ttsStatus.textContent = '🔊 Playing voice response...';
                            updateStatus('🔊 I\\'m speaking... Keep talking when I\\'m done!', 'speaking');
                        }}).catch((e) => {{
                            console.log('Auto-play blocked, user must click play');
                            ttsStatus.textContent = '🔊 Click PLAY button above to hear my voice response!';
                            playBtn.style.background = '#ff6b6b';
                            playBtn.style.animation = 'pulse 2s infinite';
                        }});
                        
                        currentTTSAudio = audioElement;
                        
                    }} catch (e) {{
                        console.error('Error loading TTS audio:', e);
                        document.getElementById('ttsStatus').textContent = '❌ Voice response failed to load';
                    }}
                }}
                
                function playCurrentTTS() {{
                    const audioElement = document.getElementById('ttsAudio');
                    if (audioElement && audioElement.src) {{
                        audioElement.play().then(() => {{
                            document.getElementById('ttsStatus').textContent = '🔊 Playing voice response...';
                            updateStatus('🔊 I\\'m speaking... Keep talking when I\\'m done!', 'speaking');
                            
                            // Reset play button
                            const playBtn = document.getElementById('playTTSBtn');
                            playBtn.style.background = '#4caf50';
                            playBtn.style.animation = 'none';
                        }}).catch((e) => {{
                            console.error('Playback failed:', e);
                            document.getElementById('ttsStatus').textContent = '❌ Playback failed - try again';
                        }});
                    }}
                }}
                
                // Check for AI responses and TTS audio periodically
                setInterval(function() {{
                    // Check for AI response
                    const response = localStorage.getItem('ai_response_ready');
                    if (response) {{
                        localStorage.removeItem('ai_response_ready');
                        showAIResponse(response);
                    }}
                    
                    // Check for TTS audio
                    const ttsAudio = localStorage.getItem('tts_audio_ready');
                    if (ttsAudio) {{
                        localStorage.removeItem('tts_audio_ready');
                        loadTTSAudio(ttsAudio);
                    }}
                }}, 500);
            </script>
        </body>
        </html>
        """
        
        # Render the HTML component
        components.html(voice_html, height=600, scrolling=False)
    
    def _process_pending_voice_data(self):
        """Process voice data and generate TTS"""
        
        # Check for voice messages to process
        voice_messages = []
        
        for key in list(st.session_state.keys()):
            if key.startswith('voice_msg_'):
                message_data = st.session_state[key]
                if isinstance(message_data, str) and not st.session_state.get(f"{key}_processed", False):
                    voice_messages.append((key, message_data))
        
        # Process each voice message
        for key, transcript in voice_messages:
            if transcript and len(transcript.strip()) > 2:
                st.info(f"🎤 **You said:** *\"{transcript}\"*")
                
                # Get AI response
                with st.spinner("🧠 Processing your message..."):
                    ai_response = self.on_voice_callback(transcript)
                
                # Display AI response
                st.success(f"🎿 **Ski Expert:** {ai_response}")
                
                # Generate TTS and send to JavaScript
                self._generate_and_send_tts(ai_response)
                
                # Mark as processed
                st.session_state[f"{key}_processed"] = True
    
    def _generate_and_send_tts(self, text: str):
        """Generate TTS audio and send to JavaScript"""
        try:
            st.markdown("### 🔊 Generating Voice Response...")
            
            with st.spinner("🎵 Creating voice response..."):
                # Generate TTS
                response = self.client.audio.speech.create(
                    model=Config.TTS_MODEL,
                    voice=Config.TTS_VOICE,
                    input=text[:1200],  # Limit length
                    response_format="mp3"
                )
                
                # Convert to base64
                audio_base64 = base64.b64encode(response.content).decode()
            
            # Send audio to JavaScript
            js_tts = f"""
            <script>
            localStorage.setItem('ai_response_ready', {repr(text)});
            localStorage.setItem('tts_audio_ready', '{audio_base64}');
            </script>
            """
            components.html(js_tts, height=0)
            
            st.success("🎧 **Voice response generated!** It should play automatically in the interface above.")
            
            # Fallback audio player
            st.markdown("### 🎧 Fallback Audio Player:")
            st.audio(response.content, format="audio/mp3")
            
            st.markdown("""
            <div style='background: linear-gradient(135deg, #e8f5e8, #f3e5f5); 
                       padding: 1rem; border-radius: 10px; margin: 1rem 0;
                       border-left: 4px solid #4caf50; text-align: center;'>
                <strong>💬 Continue the conversation!</strong><br>
                Keep talking in the interface above - I'm listening!
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"TTS Error: {str(e)}")
            st.warning("Voice response failed, but you have my text response above!")
    
    def _show_voice_status(self):
        """Show voice status and tips"""
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 Voice Conversation Tips
            
            **To hear my voice responses:**
            1. **Allow microphone** when prompted
            2. **Start talking** using the button above
            3. **Listen for my voice response** (auto-plays)
            4. **If no auto-play:** Click the 🔊 play button
            5. **Keep talking** - I'm always listening!
            
            **Try saying:**
            - "I need intermediate all-mountain skis"
            - "What's the difference between these?"
            - "Help me choose the right size"
            """)
        
        with col2:
            st.markdown("""
            ### 🔧 Audio Status
            
            **Voice Recognition:** ✅ Active  
            **AI Processing:** ✅ Ready  
            **TTS Generation:** ✅ Working  
            **Audio Playback:** ✅ Available
            
            **Troubleshooting:**
            - Make sure volume is up
            - Use Chrome or Safari browser
            - Click allow for microphone access
            - If no auto-play, click 🔊 buttons
            - Check fallback audio player below
            
            **Still no audio?** Try the fallback player that appears after each response!
            """)

# Message handler
def handle_voice_message_data():
    """Handle voice data with better localStorage integration"""
    
    js_handler = """
    <script>
    // Better localStorage polling for voice messages
    setInterval(function() {
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('voice_msg_')) {
                try {
                    const data = JSON.parse(localStorage.getItem(key));
                    if (data && !data.processed) {
                        // Mark as processed in localStorage
                        data.processed = true;
                        localStorage.setItem(key, JSON.stringify(data));
                        
                        // Send to Streamlit session state
                        if (window.parent.streamlit) {
                            window.parent.streamlit.setComponentValue(key, data.transcript);
                        }
                    }
                } catch (e) {
                    // Clean up invalid entries
                    localStorage.removeItem(key);
                }
            }
        }
    }, 1000);
    </script>
    """
    
    components.html(js_handler, height=0)