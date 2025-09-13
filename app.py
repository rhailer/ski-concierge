import streamlit as st
import openai
import sys
import os
import time
from typing import Dict, List, Any

# Setup imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from src.ski_expert import SkiExpert
    from src.continuous_voice_dialog import ContinuousVoiceDialog, handle_voice_message
    from config.settings import Config
except ImportError as e:
    st.error(f"❌ Setup Error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="🎿 Ski Concierge",
    page_icon="🎿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS (keeping all previous styles)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main > div {
        padding-top: 1rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .ski-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #1e3c72 100%);
        color: white;
        padding: 4rem 2rem;
        margin: -1rem -1rem 3rem -1rem;
        border-radius: 0 0 40px 40px;
        text-align: center;
        box-shadow: 0 10px 40px rgba(30, 60, 114, 0.3);
    }
    
    .ski-title {
        font-family: 'Playfair Display', serif;
        font-size: 4rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(45deg, #fff, #e3f2fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .ski-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.4rem;
        font-weight: 300;
        margin: 1rem 0 0 0;
        opacity: 0.95;
    }
    
    .voice-conversation {
        background: white;
        border-radius: 30px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 16px 64px rgba(0,0,0,0.08);
        border: 1px solid #f0f8ff;
    }
    
    .conversation-history {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem 0;
        margin: 2rem 0;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 25px 25px 8px 25px;
        margin: 1.5rem 0 1.5rem auto;
        max-width: 80%;
        animation: slideInRight 0.4s ease-out;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #2c3e50;
        padding: 1.5rem 2rem;
        border-radius: 25px 25px 25px 8px;
        margin: 1.5rem auto 1.5rem 0;
        max-width: 80%;
        border-left: 4px solid #1976d2;
        animation: slideInLeft 0.4s ease-out;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .voice-response-section {
        background: linear-gradient(135deg, #e8f5e8, #f3e5f5);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state"""
    defaults = {
        'ski_expert': SkiExpert(),
        'voice_dialog': None,
        'conversation_history': [],
        'current_recommendations': [],
        'voice_conversation_started': False,
        'voice_input_received': None,
        'process_voice_input': False,
        'openai_client': None,
        'last_voice_response': None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Initialize OpenAI client and voice dialog
    if not st.session_state.openai_client:
        api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
        if api_key:
            st.session_state.openai_client = openai.OpenAI(api_key=api_key)
            st.session_state.voice_dialog = ContinuousVoiceDialog(
                st.session_state.openai_client,
                handle_voice_message
            )

def process_voice_input(user_input: str):
    """Process voice input and generate response"""
    if not user_input.strip():
        return
    
    # Add to conversation history
    st.session_state.conversation_history.append({
        'role': 'user',
        'content': user_input,
        'is_voice': True,
        'timestamp': time.time()
    })
    
    try:
        # Get AI response
        ai_response, recommendations = st.session_state.ski_expert.generate_response(
            user_input,
            st.session_state.openai_client
        )
        
        # Add AI response to history
        st.session_state.conversation_history.append({
            'role': 'assistant',
            'content': ai_response,
            'recommendations': recommendations,
            'is_voice': True,
            'timestamp': time.time()
        })
        
        # Update recommendations
        st.session_state.current_recommendations = recommendations
        st.session_state.last_voice_response = ai_response
        
    except Exception as e:
        error_message = f"I apologize, I encountered an error: {str(e)}. Please try again."
        st.session_state.conversation_history.append({
            'role': 'assistant',
            'content': error_message,
            'is_voice': True,
            'timestamp': time.time()
        })
        st.session_state.last_voice_response = error_message

def render_voice_conversation():
    """Render the complete voice conversation interface"""
    st.markdown('<div class="voice-conversation">', unsafe_allow_html=True)
    
    # Voice interface
    if st.session_state.voice_dialog:
        # Check for voice input to process
        if st.session_state.get('process_voice_input') and st.session_state.get('voice_input_received'):
            process_voice_input(st.session_state.voice_input_received)
            st.session_state.process_voice_input = False
            st.session_state.voice_input_received = None
            st.rerun()
        
        # Render voice interface
        voice_input_received = st.session_state.voice_dialog.render_voice_interface()
        if voice_input_received:
            st.rerun()
        
        # Display conversation history
        if st.session_state.conversation_history:
            st.markdown("### 🗣️ Voice Conversation History")
            st.markdown('<div class="conversation-history">', unsafe_allow_html=True)
            
            for message in st.session_state.conversation_history:
                if message['role'] == 'user':
                    voice_indicator = "🎤" if message.get('is_voice') else "💬"
                    st.markdown(f"""
                    <div class="user-message">
                        {voice_indicator} {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                
                else:  # assistant
                    st.markdown(f"""
                    <div class="assistant-message">
                        🎿 {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show recommendations inline
                    if message.get('recommendations'):
                        render_voice_recommendations(message['recommendations'])
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Voice response for last message
            if st.session_state.last_voice_response and st.session_state.voice_dialog:
                st.markdown('<div class="voice-response-section">', unsafe_allow_html=True)
                st.session_state.voice_dialog.play_voice_response(st.session_state.last_voice_response)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Clear after playing
                st.session_state.last_voice_response = None
        
        # Voice conversation tips
        else:
            st.markdown("""
            <div style='text-align: center; padding: 3rem; color: #666;'>
                <h3 style='color: #1976d2; margin-bottom: 2rem;'>🎤 Ready for Voice Conversation!</h3>
                <p style='font-size: 1.2rem; line-height: 1.6; margin-bottom: 2rem;'>
                    Click the record button above or upload a voice message to start our conversation.
                    I'll respond with both text and voice!
                </p>
                
                <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                           gap: 1.5rem; margin: 2rem 0;'>
                    <div style='background: #e3f2fd; padding: 1.5rem; border-radius: 15px;'>
                        <strong>🎯 Natural Dialog</strong><br>
                        Speak naturally about your skiing
                    </div>
                    <div style='background: #e8f5e8; padding: 1.5rem; border-radius: 15px;'>
                        <strong>🔊 Voice Responses</strong><br>
                        I'll talk back to you with audio
                    </div>
                    <div style='background: #fff3e0; padding: 1.5rem; border-radius: 15px;'>
                        <strong>💬 Continuous Flow</strong><br>
                        Keep the conversation going
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_voice_recommendations(recommendations: List[Dict[str, Any]]):
    """Render recommendations in voice conversation"""
    if not recommendations:
        return
    
    st.markdown("**🎿 Here are my recommendations:**")
    
    for i, ski in enumerate(recommendations, 1):
        with st.expander(f"{i}. {ski['name']} - {ski['price_range']}", expanded=True):
            st.write(ski['description'])
            
            # Specs
            if ski.get('specs'):
                col1, col2, col3 = st.columns(3)
                specs = ski['specs']
                with col1:
                    st.metric("Length", specs.get('length', 'N/A'))
                with col2:
                    st.metric("Waist", specs.get('waist', 'N/A'))
                with col3:
                    st.metric("Radius", specs.get('radius', 'N/A'))
            
            # Retailers
            if ski.get('retailers'):
                st.write("**Where to buy:**")
                retailer_cols = st.columns(len(ski['retailers']))
                for j, (retailer, link) in enumerate(ski['retailers'].items()):
                    with retailer_cols[j]:
                        st.link_button(f"🛒 {retailer}", link, use_container_width=True)

def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="ski-header">
        <h1 class="ski-title">🎿 Ski Concierge</h1>
        <p class="ski-subtitle">Continuous voice conversation to find your perfect skis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Key check
    if not st.session_state.openai_client:
        st.error("🔑 **OpenAI API Key Required for Voice Features**")
        
        with st.expander("💡 Enter API Key"):
            temp_key = st.text_input("OpenAI API Key:", type="password")
            if temp_key and st.button("🔓 Set API Key", type="primary"):
                try:
                    client = openai.OpenAI(api_key=temp_key)
                    client.models.list()  # Test
                    
                    st.session_state.openai_client = client
                    st.session_state.voice_dialog = ContinuousVoiceDialog(
                        client, handle_voice_message
                    )
                    st.success("✅ Voice features activated!")
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Invalid API key: {str(e)}")
        st.stop()
    
    # Main layout
    voice_col, sidebar_col = st.columns([3, 1])
    
    with voice_col:
        render_voice_conversation()
    
    with sidebar_col:
        # Current recommendations summary
        if st.session_state.current_recommendations:
            st.markdown("## 🎿 Current Recommendations")
            for i, ski in enumerate(st.session_state.current_recommendations, 1):
                st.write(f"**{i}. {ski['name']}** - {ski['price_range']}")
        
        # Voice conversation controls
        st.markdown("---")
        st.markdown("## 🎤 Voice Controls")
        
        if st.button("🔄 New Voice Conversation", use_container_width=True):
            # Reset everything
            st.session_state.ski_expert.reset_conversation()
            st.session_state.conversation_history = []
            st.session_state.current_recommendations = []
            st.session_state.voice_conversation_started = False
            st.session_state.last_voice_response = None
            st.success("✨ Ready for a fresh voice conversation!")
            time.sleep(1)
            st.rerun()
        
        # Tips for voice conversation
        st.markdown("### 💡 Voice Tips")
        st.markdown("""
        - **Speak clearly** and at normal pace
        - **Ask follow-ups** like "Compare these options"
        - **Be specific** about your needs
        - **Use mobile upload** if recorder doesn't work
        """)

if __name__ == "__main__":
    main()