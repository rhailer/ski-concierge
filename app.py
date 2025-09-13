import streamlit as st
import openai
import sys
import os
import time
from typing import Dict, List

# Setup imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.ski_expert import SkiExpert
from src.enhanced_voice import EnhancedVoiceHandler
from config.settings import Config
from assets.ski_icons import SKIER_ICON, MOUNTAIN_ICON, MIC_ICON, TERRAIN_ICONS

# Page configuration
st.set_page_config(
    page_title="Ski Concierge",
    page_icon="⛷️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced Austrian-inspired CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    * {
        box-sizing: border-box;
    }
    
    .main > div {
        padding-top: 2rem;
    }
    
    .ski-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 50%, #2c3e50 100%);
        color: white;
        margin: -2rem -2rem 2rem -2rem;
        position: relative;
        overflow: hidden;
    }
    
    .ski-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='white' fill-opacity='0.03'%3E%3Cpath d='M20 20c0-11.046 8.954-20 20-20s20 8.954 20 20-8.954 20-20 20-20-8.954-20-20z'/%3E%3C/g%3E%3C/svg%3E");
    }
    
    .ski-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .ski-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        margin: 1rem 0 0 0;
        opacity: 0.95;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    
    .quick-selector-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
        padding: 2rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .selector-category {
        margin-bottom: 2rem;
    }
    
    .selector-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .quick-selector {
        background: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 12px;
        padding: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        position: relative;
        overflow: hidden;
    }
    
    .quick-selector:hover {
        border-color: #3498db;
        background: #f1f8ff;
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(52, 152, 219, 0.2);
    }
    
    .quick-selector.selected {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        border-color: #2980b9;
        box-shadow: 0 4px 20px rgba(52, 152, 219, 0.3);
    }
    
    .quick-selector.selected::after {
        content: '✓';
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        background: rgba(255,255,255,0.2);
        border-radius: 50%;
        width: 1.5rem;
        height: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .conversation-flow {
        background: white;
        border-radius: 25px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 12px 40px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
    }
    
    .message-bubble {
        margin: 1.5rem 0;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem 1.8rem;
        border-radius: 25px 25px 8px 25px;
        max-width: 85%;
        margin-left: auto;
        font-family: 'Inter', sans-serif;
        line-height: 1.5;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #2c3e50;
        padding: 1.2rem 1.8rem;
        border-radius: 25px 25px 25px 8px;
        max-width: 85%;
        margin-right: auto;
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
        border-left: 4px solid #3498db;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .recommendation-showcase {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .recommendation-showcase::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #27ae60, #2ecc71, #27ae60);
    }
    
    .recommendation-showcase:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.1);
        border-color: #3498db;
    }
    
    .ski-name {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 0 0 1rem 0;
    }
    
    .ski-price {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    .ski-description {
        color: #34495e;
        line-height: 1.7;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
    }
    
    .spec-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
        padding: 1.5rem;
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 15px;
    }
    
    .spec-item {
        text-align: center;
        padding: 1rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        font-family: 'Inter', sans-serif;
    }
    
    .spec-label {
        font-weight: 600;
        color: #7f8c8d;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .spec-value {
        font-weight: 600;
        color: #2c3e50;
        font-size: 1rem;
        margin-top: 0.25rem;
    }
    
    .retailer-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 0.75rem;
        margin: 1.5rem 0;
    }
    
    .retailer-link {
        background: linear-gradient(135deg, #00b894, #00a085);
        color: white !important;
        padding: 0.75rem 1rem;
        border-radius: 25px;
        text-decoration: none !important;
        font-size: 0.9rem;
        font-weight: 600;
        text-align: center;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        display: block;
    }
    
    .retailer-link:hover {
        background: linear-gradient(135deg, #00a085, #008f75);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
        text-decoration: none !important;
        color: white !important;
    }
    
    .profile-summary {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
    }
    
    .profile-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 0.75rem 0;
        font-weight: 500;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #3498db, #2980b9) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3) !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2980b9, #21618c) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4) !important;
    }
    
    .stSelectbox > div > div {
        border-radius: 15px !important;
        border: 2px solid #e9ecef !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextInput > div > div > input {
        border-radius: 15px !important;
        border: 2px solid #e9ecef !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 15px !important;
        border: 2px solid #e9ecef !important;
        font-family: 'Inter', sans-serif !important;
        padding: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state"""
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
            st.session_state.voice_handler = EnhancedVoiceHandler(
                client, 
                on_transcription_callback=handle_voice_input
            )
            st.session_state.openai_client = client
        else:
            st.session_state.voice_handler = None
            st.session_state.openai_client = None
    
    if 'current_recommendations' not in st.session_state:
        st.session_state.current_recommendations = []
    
    if 'last_interaction_time' not in st.session_state:
        st.session_state.last_interaction_time = time.time()

def handle_voice_input(transcription: str):
    """Handle voice input and process immediately"""
    if transcription and st.session_state.openai_client:
        process_user_input(transcription, is_voice=True)

def process_user_input(user_input: str, is_voice: bool = False):
    """Process user input and generate AI response"""
    try:
        # Update user profile with quick selections
        for key, value in st.session_state.quick_selections.items():
            if value:
                st.session_state.ski_expert.user_profile[key] = value
        
        # Generate AI response
        ai_response, recommendations = st.session_state.ski_expert.generate_response(
            user_input, 
            st.session_state.openai_client
        )
        
        st.session_state.current_recommendations = recommendations
        st.session_state.last_interaction_time = time.time()
        
        # If voice input, play audio response
        if is_voice and st.session_state.voice_handler:
            # Use threading to not block the UI
            def play_audio():
                st.session_state.voice_handler.play_response(ai_response)
            
            threading.Thread(target=play_audio, daemon=True).start()
        
        return ai_response, recommendations
        
    except Exception as e:
        st.error(f"Error processing input: {e}")
        return None, []

def render_quick_selectors():
    """Render enhanced quick selectors"""
    st.markdown('<div class="quick-selector-grid">', unsafe_allow_html=True)
    
    # Create 4 columns for categories
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="selector-title">🎿 Skill Level</div>', unsafe_allow_html=True)
        skills = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
        
        for skill in skills:
            selected = st.session_state.quick_selections['skill_level'] == skill.lower()
            button_class = "quick-selector selected" if selected else "quick-selector"
            
            if st.button(skill, key=f"skill_{skill}", help=f"I'm a {skill.lower()} skier"):
                st.session_state.quick_selections['skill_level'] = skill.lower()
                process_user_input(f"I'm a {skill.lower()} skier")
                st.rerun()
    
    with col2:
        st.markdown('<div class="selector-title">🏔️ Terrain</div>', unsafe_allow_html=True)
        terrains = [
            ('All-Mountain', 'all-mountain'),
            ('Powder', 'powder'),
            ('Carving', 'carving'),
            ('Park', 'park')
        ]
        
        for display, value in terrains:
            selected = st.session_state.quick_selections['terrain_preference'] == value
            
            if st.button(display, key=f"terrain_{value}", help=f"I prefer {display.lower()} skiing"):
                st.session_state.quick_selections['terrain_preference'] = value
                process_user_input(f"I prefer {display.lower()} skiing")
                st.rerun()
    
    with col3:
        st.markdown('<div class="selector-title">💰 Budget</div>', unsafe_allow_html=True)
        budgets = ['Under $400', '$400-600', '$600-800', '$800+']
        
        for budget in budgets:
            selected = st.session_state.quick_selections['budget_range'] == budget
            
            if st.button(budget, key=f"budget_{budget}", help=f"My budget is {budget}"):
                st.session_state.quick_selections['budget_range'] = budget
                process_user_input(f"My budget is {budget}")
                st.rerun()
    
    with col4:
        st.markdown('<div class="selector-title">⏰ Frequency</div>', unsafe_allow_html=True)
        frequencies = ['Occasional', 'Weekends', 'Weekly', 'Daily']
        
        for freq in frequencies:
            selected = st.session_state.quick_selections['skiing_frequency'] == freq.lower()
            
            if st.button(freq, key=f"freq_{freq}", help=f"I ski {freq.lower()}"):
                st.session_state.quick_selections['skiing_frequency'] = freq.lower()
                process_user_input(f"I ski {freq.lower()}")
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_conversation():
    """Render the conversation flow"""
    st.markdown('<div class="conversation-flow">', unsafe_allow_html=True)
    
    # Voice interface
    if st.session_state.voice_handler:
        new_audio = st.session_state.voice_handler.render_voice_interface()
        if new_audio:
            st.rerun()
    else:
        st.warning("🔑 Voice features require OpenAI API key. Add it to your environment or Streamlit secrets.")
    
    # Text input alternative
    st.markdown("### ✍️ Or type your message:")
    
    with st.form("text_input_form", clear_on_submit=True):
        text_input = st.text_area(
            "",
            placeholder="Tell me about your skiing experience, what terrain you love, your budget, etc...",
            height=100,
            key="text_input_area"
        )
        
        submitted = st.form_submit_button("Send Message", type="primary", use_container_width=True)
        
        if submitted and text_input:
            ai_response, recommendations = process_user_input(text_input)
            if ai_response:
                st.rerun()
    
    # Display conversation history
    if st.session_state.ski_expert.conversation_history:
        st.markdown("---")
        st.markdown("### 💬 Our Conversation")
        
        for exchange in st.session_state.ski_expert.conversation_history:
            # User message
            st.markdown(f"""
            <div class="message-bubble">
                <div class="user-message">
                    {exchange['user']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Assistant message
            st.markdown(f"""
            <div class="message-bubble">
                <div class="assistant-message">
                    {exchange['assistant']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_recommendations():
    """Render ski recommendations"""
    st.markdown("## 🎿 Your Perfect Skis")
    
    if st.session_state.current_recommendations:
        for i, ski in enumerate(st.session_state.current_recommendations, 1):
            st.markdown(f"""
            <div class="recommendation-showcase">
                <div class="ski-name">{i}. {ski['name']}</div>
                <div class="ski-price">{ski['price_range']}</div>
                <div class="ski-description">{ski['description']}</div>
                
                <div class="spec-grid">
                    <div class="spec-item">
                        <div class="spec-label">Length</div>
                        <div class="spec-value">{ski.get('specs', {}).get('length', 'N/A')}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Waist</div>
                        <div class="spec-value">{ski.get('specs', {}).get('waist', 'N/A')}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Radius</div>
                        <div class="spec-value">{ski.get('specs', {}).get('radius', 'N/A')}</div>
                    </div>
                </div>
                
                <div class="retailer-grid">
                    {"".join([f'<a href="{link}" target="_blank" class="retailer-link">{retailer}</a>' 
                            for retailer, link in ski.get('retailers', {}).items()])}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align: center; padding: 3rem; color: #7f8c8d;'>
            <h3>🎤 Ready to find your perfect skis?</h3>
            <p>Use the voice recorder above or quick selectors to tell me about your skiing!</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    initialize_session_state()
    
    # Header
    st.markdown(f"""
    <div class="ski-header">
        <h1 class="ski-title">🎿 Ski Concierge</h1>
        <p class="ski-subtitle">Natural conversation to find your perfect skis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick selectors
    render_quick_selectors()
    
    # Main layout
    conversation_col, recommendations_col = st.columns([3, 2])
    
    with conversation_col:
        render_conversation()
    
    with recommendations_col:
        render_recommendations()
        
        # User profile
        if st.session_state.ski_expert.user_profile:
            st.markdown("### 👤 Your Skiing Profile")
            profile = st.session_state.ski_expert.user_profile
            
            st.markdown('<div class="profile-summary">', unsafe_allow_html=True)
            
            profile_items = []
            if profile.get('skill_level'):
                profile_items.append(f"🎿 **Skill:** {profile['skill_level'].title()}")
            if profile.get('terrain_preference'):
                profile_items.append(f"🏔️ **Terrain:** {profile['terrain_preference'].replace('-', ' ').title()}")
            if profile.get('budget_range'):
                profile_items.append(f"💰 **Budget:** {profile['budget_range']}")
            if profile.get('skiing_frequency'):
                profile_items.append(f"⏰ **Frequency:** {profile['skiing_frequency'].title()}")
            
            for item in profile_items:
                st.markdown(f'<div class="profile-item">{item}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Reset button
        if st.button("🔄 Start Fresh Conversation", use_container_width=True):
            st.session_state.ski_expert.reset_conversation()
            st.session_state.quick_selections = {k: None for k in st.session_state.quick_selections}
            st.session_state.current_recommendations = []
            st.rerun()

if __name__ == "__main__":
    main()