import streamlit as st
import openai
import sys
import os
from typing import Dict, List

# Setup imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.ski_expert import SkiExpert
from src.continuous_voice import ContinuousVoiceHandler
from src.ui_components import render_ski_recommendations, render_quick_selectors, render_conversation_flow
from config.settings import Config
from assets.ski_icons import SKIER_ICON, MOUNTAIN_ICON, MIC_ICON, TERRAIN_ICONS

# Page configuration
st.set_page_config(
    page_title="Ski Concierge",
    page_icon="⛷️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Austrian 1980s inspired CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+Pro:wght@300;400;600&display=swap');
    
    .main-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    .ski-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #2c3e50, #34495e);
        color: white;
        margin-bottom: 2rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .ski-title {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .ski-subtitle {
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    .quick-selector {
        background: white;
        border: 2px solid #ecf0f1;
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .quick-selector:hover {
        border-color: #3498db;
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(52, 152, 219, 0.2);
    }
    
    .quick-selector.selected {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        border-color: #2980b9;
    }
    
    .conversation-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid #ecf0f1;
    }
    
    .voice-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        padding: 1rem;
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white;
        border-radius: 50px;
        margin: 1rem 0;
        font-weight: 600;
    }
    
    .voice-indicator.listening {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .message-user {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 1rem 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .message-assistant {
        background: #f8f9fa;
        color: #2c3e50;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 1rem 0;
        max-width: 80%;
        border-left: 4px solid #3498db;
    }
    
    .recommendation-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #27ae60;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
    }
    
    .recommendation-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 25px rgba(0,0,0,0.12);
    }
    
    .ski-specs {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
    }
    
    .spec-item {
        text-align: center;
        padding: 0.5rem;
        background: white;
        border-radius: 8px;
        font-size: 0.9rem;
    }
    
    .retailer-links {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .retailer-link {
        background: linear-gradient(135deg, #00b894, #00a085);
        color: white !important;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        text-decoration: none !important;
        font-size: 0.9rem;
        font-weight: 500;
        transition: transform 0.2s ease;
    }
    
    .retailer-link:hover {
        transform: scale(1.05);
        text-decoration: none !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #3498db, #2980b9) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state with enhanced tracking"""
    if 'ski_expert' not in st.session_state:
        st.session_state.ski_expert = SkiExpert()
    
    if 'quick_selections' not in st.session_state:
        st.session_state.quick_selections = {
            'skill_level': None,
            'terrain_preference': None,
            'budget_range': None,
            'skiing_frequency': None
        }
    
    if 'voice_handler' not in st.session_state:
        api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
        if api_key:
            client = openai.OpenAI(api_key=api_key)
            st.session_state.voice_handler = ContinuousVoiceHandler(
                client, 
                on_transcription_callback=handle_voice_input
            )
            st.session_state.openai_client = client
        else:
            st.session_state.voice_handler = None
            st.session_state.openai_client = None
    
    if 'conversation_active' not in st.session_state:
        st.session_state.conversation_active = False
    
    if 'current_recommendations' not in st.session_state:
        st.session_state.current_recommendations = []
    
    if 'is_listening' not in st.session_state:
        st.session_state.is_listening = False

def handle_voice_input(transcription: str):
    """Handle continuous voice input"""
    if transcription and st.session_state.openai_client:
        # Process the transcription immediately
        process_user_input(transcription, is_voice=True)

def process_user_input(user_input: str, is_voice: bool = False):
    """Process user input and generate response"""
    try:
        # Update user profile with quick selections
        if any(st.session_state.quick_selections.values()):
            for key, value in st.session_state.quick_selections.items():
                if value:
                    st.session_state.ski_expert.user_profile[key] = value
        
        # Generate AI response
        ai_response, recommendations = st.session_state.ski_expert.generate_response(
            user_input, 
            st.session_state.openai_client
        )
        
        st.session_state.conversation_active = True
        st.session_state.current_recommendations = recommendations
        
        # If voice input, immediately play response
        if is_voice and st.session_state.voice_handler:
            audio_response = st.session_state.voice_handler.text_to_speech_stream(ai_response)
            if audio_response:
                st.audio(audio_response, format="audio/mp3", autoplay=True)
        
        # Refresh the display
        st.rerun()
        
    except Exception as e:
        st.error(f"Error processing input: {e}")

def render_quick_selectors():
    """Render quick selection buttons at the top"""
    st.markdown("<div style='margin: 2rem 0;'>", unsafe_allow_html=True)
    
    # Skill Level
    st.markdown("**🎿 Skill Level**")
    skill_cols = st.columns(4)
    skills = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
    
    for i, skill in enumerate(skills):
        with skill_cols[i]:
            selected = st.session_state.quick_selections['skill_level'] == skill.lower()
            if st.button(
                skill, 
                key=f"skill_{skill}",
                help=f"Select {skill} skill level",
                type="primary" if selected else "secondary"
            ):
                st.session_state.quick_selections['skill_level'] = skill.lower()
                process_user_input(f"I'm a {skill.lower()} skier")
    
    # Terrain Preference
    st.markdown("**🏔️ Preferred Terrain**")
    terrain_cols = st.columns(4)
    terrains = [
        ('All-Mountain', 'all_mountain'),
        ('Powder', 'powder'),
        ('Carving/Groomers', 'carving'),
        ('Park/Freestyle', 'park')
    ]
    
    for i, (display, value) in enumerate(terrains):
        with terrain_cols[i]:
            selected = st.session_state.quick_selections['terrain_preference'] == value
            icon_html = TERRAIN_ICONS.get(value, MOUNTAIN_ICON)
            
            button_html = f"""
            <div class="quick-selector {'selected' if selected else ''}" 
                 onclick="selectTerrain('{value}')">
                {icon_html}
                <div style="margin-top: 0.5rem; font-weight: 600;">{display}</div>
            </div>
            """
            
            if st.button(
                display,
                key=f"terrain_{value}",
                help=f"I prefer {display.lower()} skiing",
                type="primary" if selected else "secondary"
            ):
                st.session_state.quick_selections['terrain_preference'] = value
                process_user_input(f"I prefer {display.lower()} skiing")
    
    # Budget Range
    st.markdown("**💰 Budget Range**")
    budget_cols = st.columns(4)
    budgets = ['Under $400', '$400-600', '$600-800', '$800+']
    
    for i, budget in enumerate(budgets):
        with budget_cols[i]:
            selected = st.session_state.quick_selections['budget_range'] == budget
            if st.button(
                budget,
                key=f"budget_{budget}",
                help=f"My budget is {budget}",
                type="primary" if selected else "secondary"
            ):
                st.session_state.quick_selections['budget_range'] = budget
                process_user_input(f"My budget is {budget}")
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_continuous_voice_interface():
    """Render the continuous voice interface"""
    if not st.session_state.voice_handler:
        st.warning("Voice features require OpenAI API key")
        return
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not st.session_state.is_listening:
            if st.button("🎤 Start Conversation", type="primary", use_container_width=True):
                st.session_state.is_listening = True
                st.rerun()
        else:
            # Show listening interface
            st.markdown(f"""
            <div class="voice-indicator listening">
                {MIC_ICON}
                <span>Listening... Speak naturally!</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Start continuous listening
            webrtc_ctx = st.session_state.voice_handler.start_continuous_listening()
            
            if st.button("Stop Listening", type="secondary", use_container_width=True):
                st.session_state.is_listening = False
                st.rerun()

def main():
    initialize_session_state()
    
    # Header with Austrian ski aesthetic
    st.markdown(f"""
    <div class="ski-header">
        {SKIER_ICON}
        <h1 class="ski-title">Ski Concierge</h1>
        <p class="ski-subtitle">Natural conversation to find your perfect skis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick selectors at the top
    render_quick_selectors()
    
    st.markdown("---")
    
    # Main conversation area
    conversation_col, recommendations_col = st.columns([2, 1])
    
    with conversation_col:
        st.markdown('<div class="conversation-container">', unsafe_allow_html=True)
        
        # Continuous voice interface
        render_continuous_voice_interface()
        
        # Text input as backup
        st.markdown("**💬 Or type your message:**")
        text_input = st.text_input(
            "",
            placeholder="Tell me about your skiing... What's your experience? What terrain do you love?",
            key="text_input"
        )
        
        if text_input:
            process_user_input(text_input)
            st.session_state.text_input = ""  # Clear input
        
        # Display conversation
        if st.session_state.ski_expert.conversation_history:
            st.markdown("### Our Conversation")
            
            for exchange in st.session_state.ski_expert.conversation_history:
                # User message
                st.markdown(f"""
                <div class="message-user">
                    {exchange['user']}
                </div>
                """, unsafe_allow_html=True)
                
                # Assistant message
                st.markdown(f"""
                <div class="message-assistant">
                    {exchange['assistant']}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with recommendations_col:
        st.markdown("### 🎿 Your Perfect Skis")
        
        if st.session_state.current_recommendations:
            for i, ski in enumerate(st.session_state.current_recommendations, 1):
                st.markdown(f"""
                <div class="recommendation-card">
                    <h4 style="color: #2c3e50; margin: 0 0 1rem 0;">
                        {i}. {ski['name']}
                    </h4>
                    
                    <div style="color: #e74c3c; font-weight: 600; font-size: 1.1rem; margin-bottom: 1rem;">
                        💰 {ski['price_range']}
                    </div>
                    
                    <p style="color: #34495e; line-height: 1.6;">
                        {ski['description']}
                    </p>
                    
                    <div class="ski-specs">
                        <div class="spec-item">
                            <strong>Length</strong><br>
                            {ski.get('specs', {}).get('length', 'N/A')}
                        </div>
                        <div class="spec-item">
                            <strong>Waist</strong><br>
                            {ski.get('specs', {}).get('waist', 'N/A')}
                        </div>
                        <div class="spec-item">
                            <strong>Radius</strong><br>
                            {ski.get('specs', {}).get('radius', 'N/A')}
                        </div>
                    </div>
                    
                    <div class="retailer-links">
                        {"".join([f'<a href="{link}" target="_blank" class="retailer-link">{retailer}</a>' 
                                for retailer, link in ski.get('retailers', {}).items()])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🗣️ Start talking or select your preferences above, and I'll find your perfect skis!")
        
        # User profile summary
        if st.session_state.ski_expert.user_profile:
            st.markdown("### 👤 Your Profile")
            profile = st.session_state.ski_expert.user_profile
            
            profile_items = []
            if profile.get('skill_level'):
                profile_items.append(f"**Skill:** {profile['skill_level'].title()}")
            if profile.get('terrain_preference'):
                profile_items.append(f"**Terrain:** {profile['terrain_preference'].replace('_', ' ').title()}")
            if profile.get('budget'):
                profile_items.append(f"**Budget:** {profile['budget']}")
            
            if profile_items:
                st.markdown("<br>".join(profile_items), unsafe_allow_html=True)
        
        # Reset button
        if st.button("🔄 Start Over", use_container_width=True):
            st.session_state.ski_expert.reset_conversation()
            st.session_state.quick_selections = {k: None for k in st.session_state.quick_selections}
            st.session_state.conversation_active = False
            st.session_state.current_recommendations = []
            st.rerun()

if __name__ == "__main__":
    main()