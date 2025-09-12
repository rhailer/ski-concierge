# Test each import individually
try:
    import speech_recognition as sr
    print("✅ speech_recognition imported successfully")
except ImportError as e:
    print(f"❌ speech_recognition failed: {e}")

try:
    from gtts import gTTS
    print("✅ gTTS imported successfully")
except ImportError as e:
    print(f"❌ gTTS failed: {e}")

try:
    import pygame
    print("✅ pygame imported successfully")
except ImportError as e:
    print(f"❌ pygame failed: {e}")

try:
    import pyaudio
    print("✅ pyaudio imported successfully")
except ImportError as e:
    print(f"❌ pyaudio failed: {e}")

try:
    import streamlit as st
    print("✅ streamlit imported successfully")
except ImportError as e:
    print(f"❌ streamlit failed: {e}")

try:
    import openai
    print("✅ openai imported successfully")
except ImportError as e:
    print(f"❌ openai failed: {e}")