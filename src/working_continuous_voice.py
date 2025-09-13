import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os
import base64
import time
from typing import Callable
from config.settings import Config

class WorkingContinuousVoice:
    def __init__(self, openai_client, on_voice_callback: Callable[[str], str]):
        self.client = openai_client
        self.on_voice_callback = on_voice_callback
        
    def render_continuous_voice_dialog(self):
        """Render working continuous voice dialog"""
        
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
        
        # Create the working voice interface
        self._render_voice_interface()
        
        # Handle any pending voice processing
        self._process_pending_voice_data()
        
        # Show conversation tips
        self._show_voice_tips()
    
    def _render_voice_interface(self):
        """Render the actual voice interface"""
        
        # Voice interface using session state for communication
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
                    max-width: 600px;
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
                    animation: pulse 2s infinite;
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
                }}
                
                @keyframes fadeIn {{
                    from {{ opacity: 0; transform: translateY(10px); }}
                    to {{ opacity: 1; transform: translateY(0); }}
                }}
            </style>
        </head>
        <body>
            <div class="voice-container">
                <div id="status" class="status">
                    🎤 Ready to start voice conversation
                </div>
                
                <button id="voiceBtn" class="voice-btn" onclick="toggleVoice()">
                    🎤 Start Talking
                </button>
                
                <div id="conversation" class="conversation"></div>
            </div>
            
            <script>
                let isListening = false;
                let recognition = null;
                let conversationCount = 0;
                
                // Initialize speech recognition
                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    recognition = new SpeechRecognition();
                    recognition.continuous = true;
                    recognition.interimResults = false;
                    recognition.lang = 'en-US';
                    
                    recognition.onstart = function() {{
                        updateStatus('🎤 Listening... Start talking!');
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
                        updateStatus('❌ Error: ' + event.error + '. Click to try again.');
                        resetVoiceButton();
                    }};
                    
                    recognition.onend = function() {{
                        if (isListening) {{
                            // Restart recognition for continuous listening
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
                    updateStatus('❌ Speech recognition not supported. Please use text input below.');
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
                    
                    try {{
                        recognition.start();
                    }} catch(e) {{
                        console.error('Failed to start recognition:', e);
                        updateStatus('❌ Failed to start. Please try again.');
                        resetVoiceButton();
                    }}
                }}
                
                function stopListening() {{
                    isListening = false;
                    if (recognition) {{
                        recognition.stop();
                    }}
                    resetVoiceButton();
                    updateStatus('👋 Voice conversation stopped. Click to resume.');
                }}
                
                function resetVoiceButton() {{
                    isListening = false;
                    document.getElementById('voiceBtn').textContent = '🎤 Start Talking';
                    document.getElementById('voiceBtn').classList.remove('listening');
                }}
                
                function processVoiceInput(transcript) {{
                    updateStatus('🧠 Processing: "' + transcript + '"...');
                    addMessage('user', transcript);
                    
                    // Send to Streamlit using a unique key
                    const messageKey = 'voice_msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                    localStorage.setItem(messageKey, JSON.stringify({{
                        transcript: transcript,
                        timestamp: Date.now(),
                        processed: false
                    }}));
                    
                    // Trigger Streamlit update
                    window.parent.postMessage({{
                        type: 'VOICE_MESSAGE',
                        key: messageKey,
                        transcript: transcript
                    }}, '*');
                    
                    conversationCount++;
                }}
                
                function addMessage(sender, text) {{
                    const conversation = document.getElementById('conversation');
                    const msgDiv = document.createElement('div');
                    msgDiv.className = `message ${{sender}}-msg`;
                    
                    const prefix = sender === 'user' ? '🗣️ You: ' : '🎿 Ski Expert: ';
                    msgDiv.textContent = prefix + text;
                    
                    conversation.appendChild(msgDiv);
                    conversation.scrollTop = conversation.scrollHeight;
                }}
                
                function updateStatus(message) {{
                    document.getElementById('status').textContent = message;
                }}
                
                function showAIResponse(response) {{
                    addMessage('ai', response);
                    updateStatus('🎤 Got it! Keep talking or ask follow-up questions...');
                }}
                
                // Listen for AI responses from Streamlit
                window.addEventListener('message', function(event) {{
                    if (event.data.type === 'AI_RESPONSE') {{
                        showAIResponse(event.data.response);
                    }}
                }});
                
                // Check for stored responses periodically
                setInterval(function() {{
                    const response = localStorage.getItem('ai_response_ready');
                    if (response) {{
                        localStorage.removeItem('ai_response_ready');
                        showAIResponse(response);
                    }}
                }}, 500);
            </script>
        </body>
        </html>
        """
        
        # Render the HTML component
        components.html(voice_html, height=500, scrolling=False)
    
    def _process_pending_voice_data(self):
        """Process any pending voice data from localStorage"""
        
        # Check if there are voice messages to process
        voice_messages = []
        
        # Check session state for voice messages (from JavaScript)
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
                
                # Play TTS response
                self._play_tts_response(ai_response)
                
                # Mark as processed
                st.session_state[f"{key}_processed"] = True
                
                # Send response back to JavaScript
                js_response = f"""
                <script>
                localStorage.setItem('ai_response_ready', {repr(ai_response)});
                </script>
                """
                components.html(js_response, height=0)
        
        # Clean up old processed messages
        keys_to_remove = []
        for key in st.session_state.keys():
            if key.startswith('voice_msg_') and st.session_state.get(f"{key}_processed", False):
                # Keep only recent messages
                if len(keys_to_remove) > 5:  # Keep last 5 conversations
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
            if f"{key}_processed" in st.session_state:
                del st.session_state[f"{key}_processed"]
    
    def _play_tts_response(self, text: str):
        """Play TTS response with better error handling"""
        try:
            st.markdown("### 🔊 My Voice Response:")
            
            # Generate TTS
            with st.spinner("🎵 Generating voice response..."):
                response = self.client.audio.speech.create(
                    model=Config.TTS_MODEL,
                    voice=Config.TTS_VOICE,
                    input=text[:1200],  # Limit length
                    response_format="mp3"
                )
            
            # Play the audio with autoplay
            st.audio(response.content, format="audio/mp3", autoplay=True)
            
            # Show success message
            st.success("🎧 **Voice response playing!** Keep talking for more questions.")
            
            # Encourage continuation
            st.markdown("""
            <div style='background: linear-gradient(135deg, #e8f5e8, #f3e5f5); 
                       padding: 1rem; border-radius: 10px; margin: 1rem 0;
                       border-left: 4px solid #4caf50; text-align: center;'>
                <strong>💬 Continue the conversation!</strong><br>
                Keep talking or ask follow-up questions about the ski recommendations.
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.warning(f"Voice response not available ({str(e)}), but you have my text response above!")
    
    def _show_voice_tips(self):
        """Show helpful voice conversation tips"""
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 Voice Conversation Tips
            
            **Get Started:**
            - "I need help finding skis for intermediate skiing"
            - "I'm looking for powder skis under $700"
            
            **Ask Follow-ups:**
            - "What's the difference between these options?"
            - "Which would be better for my height?"
            - "Show me something in a different price range"
            
            **Get Specific Help:**
            - "Help me choose between these two"
            - "What size should I get?"
            - "Tell me more about that first recommendation"
            """)
        
        with col2:
            st.markdown("""
            ### 🔧 Troubleshooting
            
            **If voice isn't working:**
            - Make sure you're using Chrome or Safari
            - Click "Allow" when prompted for microphone access
            - Speak clearly and wait for responses
            - Try the quick example buttons below
            
            **Technical Status:**
            - ✅ Speech Recognition: Browser-based
            - ✅ AI Processing: OpenAI GPT-4  
            - ✅ Voice Response: OpenAI TTS
            - ✅ Continuous Dialog: Active
            
            **Having Issues?** Try the quick examples below to test the system.
            """)

# Simple message handler for voice data
def handle_voice_message_data():
    """Handle voice message data from JavaScript"""
    
    # JavaScript to capture voice messages and store them in Streamlit session state
    js_handler = """
    <script>
    // Handle voice messages from the main interface
    window.addEventListener('message', function(event) {
        if (event.data.type === 'VOICE_MESSAGE') {
            // Store in a way that Streamlit can access
            const key = event.data.key;
            const transcript = event.data.transcript;
            
            // Use Streamlit's session state mechanism
            if (window.parent.streamlit) {
                window.parent.streamlit.setComponentValue(key, transcript);
            }
        }
    });
    
    // Periodic check for voice data in localStorage
    setInterval(function() {
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('voice_msg_')) {
                try {
                    const data = JSON.parse(localStorage.getItem(key));
                    if (data && !data.processed) {
                        // Mark as processed
                        data.processed = true;
                        localStorage.setItem(key, JSON.stringify(data));
                        
                        // Send to Streamlit
                        if (window.parent.streamlit) {
                            window.parent.streamlit.setComponentValue(key, data.transcript);
                        }
                    }
                } catch (e) {
                    console.error('Error processing voice message:', e);
                }
            }
        }
    }, 1000);
    </script>
    """
    
    # Render the handler
    components.html(js_handler, height=0)