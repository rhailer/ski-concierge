import streamlit as st
import time
from typing import Optional, List, Dict, Any
from config.settings import Config

class EnhancedTextInterface:
    def __init__(self, openai_client):
        self.client = openai_client
        self.conversation_starters = [
            "I'm a beginner looking for my first skis",
            "I ski powder in Colorado 20+ days a year",
            "I need carving skis under $600",
            "What's the difference between all-mountain and powder skis?",
            "I'm intermediate and want to progress to advanced terrain",
            "I ski mostly groomed runs on the East Coast"
        ]
    
    def render_conversation_interface(self) -> Optional[str]:
        """Render enhanced conversation interface with smart prompts"""
        
        # Welcome message for new users
        if 'conversation_started' not in st.session_state or not st.session_state.conversation_started:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #74b9ff, #0984e3); 
                       color: white; padding: 2rem; border-radius: 20px; text-align: center; margin: 2rem 0;'>
                <h3 style='margin: 0 0 1rem 0; font-weight: 600;'>👋 Hi! I'm your Ski Concierge</h3>
                <p style='margin: 0; opacity: 0.9; font-size: 1.1rem; line-height: 1.5;'>
                    I have 20+ years of experience matching skiers with their perfect equipment.<br>
                    Let's have a conversation to find your ideal skis!
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Smart conversation starters
        st.markdown("### 💡 Quick Start - Tell me about your skiing:")
        
        starter_cols = st.columns(2)
        for i, starter in enumerate(self.conversation_starters):
            col = starter_cols[i % 2]
            with col:
                if st.button(f"💬 {starter}", key=f"starter_{i}", help="Click to use this prompt"):
                    return starter
        
        st.markdown("---")
        
        # Main text interface
        st.markdown("### ✍️ Or describe your skiing in your own words:")
        
        # Enhanced text area with smart placeholders
        placeholder_text = self._get_smart_placeholder()
        
        with st.form("main_conversation", clear_on_submit=True):
            user_input = st.text_area(
                "",
                placeholder=placeholder_text,
                height=120,
                key="main_text_area",
                help="Tell me about your experience, preferred terrain, budget, physical stats, etc."
            )
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button(
                    "🎿 Get My Ski Recommendations", 
                    type="primary", 
                    use_container_width=True
                )
            
            if submitted and user_input.strip():
                return user_input.strip()
        
        return None
    
    def _get_smart_placeholder(self) -> str:
        """Generate smart placeholder based on current profile"""
        profile = st.session_state.get('ski_expert', {}).user_profile if hasattr(st.session_state.get('ski_expert', {}), 'user_profile') else {}
        
        if not profile:
            return """Example: "I'm an intermediate skier who loves groomed runs and wants to try powder. I ski about 10 days a year in Colorado. My budget is around $500-700. I'm 5'8" and weigh 160lbs. Currently using 10-year-old rental skis and ready for an upgrade!" """
        
        missing_info = []
        if not profile.get('skill_level'):
            missing_info.append("skill level")
        if not profile.get('terrain_preference'):
            missing_info.append("preferred terrain")
        if not profile.get('budget'):
            missing_info.append("budget range")
        if not profile.get('physical_stats'):
            missing_info.append("height/weight")
        
        if missing_info:
            return f"Tell me more about: {', '.join(missing_info)}. Any other specific needs or questions?"
        else:
            return "What other questions do you have? Want to compare specific models or need more details?"
    
    def create_audio_response(self, text: str) -> Optional[bytes]:
        """Create TTS audio response"""
        try:
            # Keep TTS for when users want it, but make it optional
            response = self.client.audio.speech.create(
                model=Config.TTS_MODEL,
                voice=Config.TTS_VOICE,
                input=text,
                response_format="mp3"
            )
            return response.content
        except Exception as e:
            # Don't fail if TTS doesn't work
            print(f"TTS not available: {e}")
            return None
    
    def offer_audio_response(self, text: str):
        """Offer audio response as an option"""
        if st.button("🔊 Hear my response", key="audio_response"):
            with st.spinner("🎵 Creating audio response..."):
                audio_bytes = self.create_audio_response(text)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                    st.success("🎧 Audio ready! Click play above.")
                else:
                    st.warning("Audio not available right now, but you have my text response!")

class SmartFollowUp:
    """Generate smart follow-up questions based on conversation state"""
    
    @staticmethod
    def generate_follow_ups(user_profile: Dict[str, Any], last_response: str) -> List[str]:
        """Generate contextual follow-up questions"""
        follow_ups = []
        
        # Based on what's missing from profile
        if not user_profile.get('skill_level'):
            follow_ups.append("What's your skiing ability level?")
        
        if not user_profile.get('terrain_preference'):
            follow_ups.append("What type of terrain do you prefer?")
        
        if not user_profile.get('budget'):
            follow_ups.append("What's your budget range?")
        
        if not user_profile.get('physical_stats'):
            follow_ups.append("What's your height and weight?")
        
        if not user_profile.get('skiing_frequency'):
            follow_ups.append("How often do you ski?")
        
        # Smart contextual questions
        if "powder" in last_response.lower():
            follow_ups.append("Do you ski mostly powder or mixed conditions?")
        
        if "carving" in last_response.lower():
            follow_ups.append("Do you prefer short or long radius turns?")
        
        if "beginner" in last_response.lower():
            follow_ups.append("Are you looking for skis to grow into or easy to learn on?")
        
        # Always useful questions
        follow_ups.extend([
            "Any specific ski brands you prefer or want to avoid?",
            "Do you have any physical considerations (knee issues, etc.)?",
            "Where do you typically ski?",
            "What don't you like about your current skis?"
        ])
        
        return follow_ups[:6]  # Return top 6 most relevant