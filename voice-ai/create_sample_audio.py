import pyttsx3
import os

os.makedirs("tests/sample_audio", exist_ok=True)

engine = pyttsx3.init()
engine.save_to_file(
    "Hello, my package has not arrived. Can you help me?",
    "tests/sample_audio/sample.wav"
)
engine.runAndWait()

print("Sample audio created at tests/sample_audio/sample.wav")