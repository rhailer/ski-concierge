import asyncio
import queue
import threading
import time
from typing import Optional, Callable
import streamlit as st
import numpy as np
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import openai
from config.settings import Config

class ContinuousVoiceHandler:
    def __init__(self, openai_client, on_transcription_callback: Callable[[str], None]):
        self.client = openai_client
        self.on_transcription = on_transcription_callback
        self.audio_buffer = queue.Queue()
        self.is_listening = False
        self.silence_threshold = 0.01
        self.min_audio_length = 1.0  # seconds
        self.max_silence_duration = 2.0  # seconds
        
    def start_continuous_listening(self):
        """Start continuous voice listening with WebRTC"""
        
        def audio_frame_callback(frame: av.AudioFrame) -> av.AudioFrame:
            audio_array = frame.to_ndarray()
            
            # Check for voice activity
            volume = np.sqrt(np.mean(audio_array**2))
            
            if volume > self.silence_threshold:
                self.audio_buffer.put((audio_array, time.time()))
                if not self.is_listening:
                    self.is_listening = True
                    threading.Thread(target=self._process_audio_buffer, daemon=True).start()
            
            return frame
        
        webrtc_ctx = webrtc_streamer(
            key="continuous-voice",
            mode=WebRtcMode.SENDONLY,
            audio_frame_callback=audio_frame_callback,
            rtc_configuration=RTCConfiguration(
                {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
            ),
            media_stream_constraints={
                "video": False,
                "audio": {
                    "echoCancellation": True,
                    "noiseSuppression": True,
                    "autoGainControl": True,
                }
            },
            async_processing=True,
        )
        
        return webrtc_ctx
    
    def _process_audio_buffer(self):
        """Process audio buffer when speech is detected"""
        audio_chunks = []
        last_audio_time = time.time()
        
        while self.is_listening:
            try:
                # Get audio from buffer
                audio_data, timestamp = self.audio_buffer.get(timeout=0.1)
                audio_chunks.append(audio_data)
                last_audio_time = timestamp
                
            except queue.Empty:
                # Check if we've had enough silence to process
                if time.time() - last_audio_time > self.max_silence_duration:
                    if len(audio_chunks) > 0:
                        self._transcribe_audio_chunks(audio_chunks)
                        audio_chunks = []
                    self.is_listening = False
                    break
        
    def _transcribe_audio_chunks(self, audio_chunks):
        """Transcribe collected audio chunks"""
        if not audio_chunks:
            return
            
        try:
            # Combine audio chunks
            combined_audio = np.concatenate(audio_chunks)
            
            # Convert to the format expected by OpenAI
            # This is a simplified version - you'd need proper audio processing
            import tempfile
            import wave
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                # Save audio as WAV file
                with wave.open(tmp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(16000)
                    wav_file.writeframes((combined_audio * 32767).astype(np.int16).tobytes())
                
                # Transcribe
                with open(tmp_file.name, "rb") as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model=Config.VOICE_MODEL,
                        file=audio_file,
                        response_format="text"
                    )
                
                # Clean up
                import os
                os.unlink(tmp_file.name)
                
                # Callback with transcription
                if transcript.strip():
                    self.on_transcription(transcript.strip())
                    
        except Exception as e:
            print(f"Error transcribing audio: {e}")
    
    def text_to_speech_stream(self, text: str):
        """Stream TTS response for immediate playback"""
        try:
            response = self.client.audio.speech.create(
                model=Config.TTS_MODEL,
                voice=Config.TTS_VOICE,
                input=text,
                response_format="mp3"
            )
            
            return response.content
            
        except Exception as e:
            print(f"Error in TTS: {e}")
            return None