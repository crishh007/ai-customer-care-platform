# ASSIGNED TO: AI-5
# Speech to Text Module
# Purpose: Convert audio input to text using Whisper API
#
# Implement:
#   - transcribe_audio(audio_file_path) → text string
#   - Support: mp3, wav, webm formats
#   - Use: OpenAI Whisper API
#   - Handle errors (file not found, API error)

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def transcribe_audio(audio_file_path: str) -> str:
    # TODO: Open audio file
    # TODO: Call openai.audio.transcriptions.create()
    # TODO: Return transcribed text
    pass
