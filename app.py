import streamlit as st
import openai
import sys
import os
import time

# Setup imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from src.ski_expert import SkiExpert
    from src.simple_voice import SimpleVoiceHandler
    from config.settings import Config
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all files are in the correct directories")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="🎿 Ski Concierge",
    page_icon="🎿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with Austrian ski aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    .main > div {
        padding-top: 1rem;
    }
    
    .ski-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 50%, #2c3e50 100%);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 30px 30px;
        position: relative;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }
    
    .ski-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, #fff, #ecf0f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .ski-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        margin: 1rem 0 0 0;
        opacity: 0.9;
        font-weight: 300;
    }
    
    .selector-section {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
    }
    
    .selector-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .button-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .selector-button {
        padding: 1rem;
        border: 2px solid #e9ecef;
        border-radius: 15px;
        background: #f8f9fa;
        color: #2c3e50;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        text-align: center;
        position: relative;
    }
    
    .selector-button:hover {
        border-color: #3498db;
        background: #ebf3fd;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.2);
    }
    
    .selector-button.selected {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        border-color: #2980b9;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    }
    
    .selector-button.selected::after {
        content: '✓';
        position: absolute;
        top: 0.5rem;
        right: 0.75rem;
        font-weight: bold;
        font-size: 1rem;
    }
    
    .conversation-card {
        background: white;
        border-radius: 25px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 12px 48px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
    }
    
    .message-container {
        margin: 2rem 0;
    }
    
    .user-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 25px 25px 8px 25px;
        margin: 1rem 0 1rem auto;
        max-width: 80%;
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        animation: slideInRight 0.3s ease-out;
    }
    
    .assistant-bubble {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #2c3e50;
        padding: 1.5rem 2rem;
        border-radius: 25px 25px 25px 8px;
        margin: 1rem auto 1rem 0;
        max-width: 80%;
        font-family: 'Inter', sans-serif;
        line-height: 1.7;
        border-left: 4px solid #3498db;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        animation: slideInLeft 0.3s ease-out;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .recommendation-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border-top: 4px solid #27ae60;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .recommendation-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #27ae60, #2ecc71, #27ae60);
        animation: shimmer 2s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .recommendation-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 16px 48px rgba(0,0,0,0.15);
    }
    
    .ski-name {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 0 0 1rem 0;
        line-height: 1.3;
    }
    
    .ski-price {
        display: inline-block;
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
    }
    
    .ski-description {
        color: #34495e;
        line-height: 1.8;
        margin: 1.5rem 0;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
    }
    
    .specs-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 2rem 0;
        padding: 1.5rem;
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 15px;
    }
    
    .spec-card {
        background: white;
        padding: 1.5rem 1rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        font-family: 'Inter', sans-serif;
    }
    
    .spec-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .spec-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
    }
    
    .retailers-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .retailer-button {
        display: block;
        background: linear-gradient(135deg, #00b894, #00a085);
        color: white !important;
        padding: 1rem;
        border-radius: 25px;
        text-decoration: none !important;
        font-weight: 600;
        text-align: center;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 4px 15px rgba(0, 184, 148, 0.3);
    }
    
    .retailer-button:hover {
        background: linear-gradient(135deg, #00a085, #008f75);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 184, 148, 0.4);
        text-decoration: none !important;
        color: white !important;
    }
    
    .profile-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .profile-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 1rem 0;
        font-weight: 500;
        font-size: 1rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #3498db, #2980b9) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(52, 152, 219, 0.3) !important;
        font-size: 1rem !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2980b9, #21618c) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 30px rgba(52, 152, 219, 0.4) !important;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 20px !important;
        border: 2px solid #e9ecef !important;
        font-family: 'Inter', sans-serif !important;
        padding: 1.5rem !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #3498db !important;
        box-shadow: 0 0 20px rgba(52, 152, 219, 0.2) !important;
    }
    
    .upload-section {
        border: 2px dashed #3498db;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        background: linear-gradient(135deg, #f8f9fa, #ffffff);
    }
    
    .upload-section:hover {
        border-color: #2980b9;
        background: linear-gradient(135deg, #ebf3fd, #f8f9fa);
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
            st.session_state.voice_handler = SimpleVoiceHandler(client)
            st.session_state.openai_client = client
        else:
            st.session_state.voice_handler = None
            st.session_state.openai_client = None
    
    if 'current_recommendations' not in st.session_state:
        st.session_state.current_recommendations = []
    
    if 'last_voice_input' not in st.session_state:
        st.session_state.last_voice_input = None

def process_user_input(user_input: str, is_voice: bool = False):
    """Process user input and generate response"""
    if not user_input.strip():
        return None, []
    
    try:
        # Update user profile with quick selections
        for key, value in st.session_state.quick_selections.items():
            if value and value != st.session_state.ski_expert.user_profile.get(key):
                st.session_state.ski_expert.user_profile[key] = value
        
        # Generate AI response
        ai_response, recommendations = st.session_state.ski_expert.generate_response(
            user_input, 
            st.session_state.openai_client
        )
        
        st.session_state.current_recommendations = recommendations
        
        # If voice input, create audio response
        if is_voice and st.session_state.voice_handler:
            st.session_state.voice_handler.play_response(ai_response)
        
        return ai_response, recommendations
        
    except Exception as e:
        st.error(f"Error processing input: {e}")
        return None, []

def render_quick_selectors():
    """Render quick selection interface"""
    st.markdown('<div class="selector-section">', unsafe_allow_html=True)
    
    # Skill Level
    st.markdown('<div class="selector-title">🎿 What\'s your skiing level?</div>', unsafe_allow_html=True)
    skill_cols = st.columns(4)
    skills = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
    
    for i, skill in enumerate(skills):
        with skill_cols[i]:
            selected = st.session_state.quick_selections['skill_level'] == skill.lower()
            if st.button(skill, key=f"skill_{skill}", type="primary" if selected else "secondary"):
                st.session_state.quick_selections['skill_level'] = skill.lower()
                process_user_input(f"I'm a {skill.lower()} skier")
                st.rerun()
    
    st.markdown("---")
    
    # Terrain Preference
    st.markdown('<div class="selector-title">🏔️ What terrain do you prefer?</div>', unsafe_allow_html=True)
    terrain_cols = st.columns(4)
    terrains = [
        ('All-Mountain', 'all-mountain'),
        ('Powder', 'powder'),
        ('Carving/Groomers', 'carving'),
        ('Park/Freestyle', 'park')
    ]
    
    for i, (display, value) in enumerate(terrains):
        with terrain_cols[i]:
            selected = st.session_state.quick_selections['terrain_preference'] == value
            if st.button(display, key=f"terrain_{value}", type="primary" if selected else "secondary"):
                st.session_state.quick_selections['terrain_preference'] = value
                process_user_input(f"I prefer {display.lower()} skiing")
                st.rerun()
    
    st.markdown("---")
    
    # Budget Range
    st.markdown('<div class="selector-title">💰 What\'s your budget?</div>', unsafe_allow_html=True)
    budget_cols = st.columns(4)
    budgets = ['Under $400', '$400-600', '$600-800', '$800+']
    
    for i, budget in enumerate(budgets):
        with budget_cols[i]:
            selected = st.session_state.quick_selections['budget_range'] == budget
            if st.button(budget, key=f"budget_{budget}", type="primary" if selected else "secondary"):
                st.session_state.quick_selections['budget_range'] = budget
                process_user_input(f"My budget is {budget}")
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_conversation_interface():
    """Render conversation interface"""
    st.markdown('<div class="conversation-card">', unsafe_allow_html=True)
    
    # Voice interface
    if st.session_state.voice_handler:
        voice_transcription = st.session_state.voice_handler.render_voice_interface()
        if voice_transcription and voice_transcription != st.session_state.last_voice_input:
            st.session_state.last_voice_input = voice_transcription
            process_user_input(voice_transcription, is_voice=True)
            st.rerun()
    
    st.markdown("---")
    
    # Text interface
    st.markdown("### ✍️ Or tell me in text:")
    
    # Example prompts
    st.markdown("**💡 Try one of these:**")
    example_cols = st.columns(2)
    
    examples = [
        "I'm looking for my first pair of skis",
        "I ski powder 20+ days a year in Colorado", 
        "I need carving skis under $500",
        "What's the difference between these options?"
    ]
    
    for i, example in enumerate(examples):
        col = example_cols[i % 2]
        with col:
            if st.button(f"💬 {example}", key=f"example_{i}"):
                process_user_input(example)
                st.rerun()
    
    # Text area
    with st.form("conversation_form", clear_on_submit=True):
        text_input = st.text_area(
            "",
            placeholder="Tell me about your skiing experience, what terrain you love, your budget, specific needs...",
            height=120,
            key="main_text_input"
        )
        
        submitted = st.form_submit_button("💬 Send Message", type="primary", use_container_width=True)
        
        if submitted and text_input:
            process_user_input(text_input.strip())
            st.rerun()
    
    # Display conversation
    if st.session_state.ski_expert.conversation_history:
        st.markdown("### 🗨️ Our Conversation")
        
        for exchange in st.session_state.ski_expert.conversation_history:
            st.markdown(f"""
            <div class="message-container">
                <div class="user-bubble">
                    {exchange['user']}
                </div>
                <div class="assistant-bubble">
                    {exchange['assistant']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_recommendations():
    """Render ski recommendations"""
    if st.session_state.current_recommendations:
        st.markdown("## 🎿 Your Perfect Ski Matches")
        
        for i, ski in enumerate(st.session_state.current_recommendations, 1):
            st.markdown(f"""
            <div class="recommendation-card">
                <div class="ski-name">{i}. {ski['name']}</div>
                <div class="ski-price">{ski['price_range']}</div>
                <div class="ski-description">{ski['description']}</div>
                
                <div class="specs-container">
                    <div class="spec-card">
                        <div class="spec-label">Length Range</div>
                        <div class="spec-value">{ski.get('specs', {}).get('length', 'N/A')}</div>
                    </div>
                    <div class="spec-card">
                        <div class="spec-label">Waist Width</div>
                        <div class="spec-value">{ski.get('specs', {}).get('waist', 'N/A')}</div>
                    </div>
                    <div class="spec-card">
                        <div class="spec-label">Turn Radius</div>
                        <div class="spec-value">{ski.get('specs', {}).get('radius', 'N/A')}</div>
                    </div>
                </div>
                
                <div class="retailers-container">
                    {"".join([f'<a href="{link}" target="_blank" class="retailer-button">Buy at {retailer}</a>' 
                            for retailer, link in ski.get('retailers', {}).items()])}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align: center; padding: 4rem 2rem; color: #7f8c8d;'>
            <h2 style='color: #34495e; margin-bottom: 1rem;'>🎿 Ready to find your perfect skis?</h2>
            <p style='font-size: 1.2rem; line-height: 1.6;'>
                Use the quick selectors above or start a conversation!<br>
                I'll help you find exactly what you need.
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_user_profile():
    """Render user profile summary"""
    if st.session_state.ski_expert.user_profile:
        st.markdown("### 👤 Your Skiing Profile")
        profile = st.session_state.ski_expert.user_profile
        
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        
        profile_items = []
        if profile.get('skill_level'):
            profile_items.append(f"🎿 **Skill Level:** {profile['skill_level'].title()}")
        if profile.get('terrain_preference'):
            profile_items.append(f"🏔️ **Preferred Terrain:** {profile['terrain_preference'].replace('-', ' ').title()}")
        if profile.get('budget_range'):
            profile_items.append(f"💰 **Budget:** {profile['budget_range']}")
        if profile.get('skiing_frequency'):
            profile_items.append(f"⏰ **Skiing Frequency:** {profile['skiing_frequency'].title()}")
        
        for item in profile_items:
            st.markdown(f'<div class="profile-item">{item}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="ski-header">
        <h1 class="ski-title">🎿 Ski Concierge</h1>
        <p class="ski-subtitle">Find your perfect skis through natural conversation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Key check
    if not st.session_state.openai_client:
        st.error("🔑 OpenAI API key required!")
        st.info("Please set your OPENAI_API_KEY environment variable or add it to Streamlit secrets.")
        
        with st.expander("💡 Enter API Key Temporarily"):
            temp_key = st.text_input("OpenAI API Key:", type="password")
            if temp_key and st.button("Set API Key"):
                client = openai.OpenAI(api_key=temp_key)
                st.session_state.voice_handler = SimpleVoiceHandler(client)
                st.session_state.openai_client = client
                st.success("✅ API key set! Refresh to continue.")
        st.stop()
    
    # Quick selectors
    render_quick_selectors()
    
    # Main layout
    conv_col, rec_col = st.columns([3, 2])
    
    with conv_col:
        render_conversation_interface()
    
    with rec_col:
        render_recommendations()
        render_user_profile()
        
        # Reset button
        if st.button("🔄 Start Fresh", use_container_width=True):
            # Clear everything
            st.session_state.ski_expert.reset_conversation()
            st.session_state.quick_selections = {k: None for k in st.session_state.quick_selections}
            st.session_state.current_recommendations = []
            st.session_state.last_voice_input = None
            st.rerun()

if __name__ == "__main__":
    main()