# Sample Audio Files

Place your test audio files here for the speech-to-text tests.

## Required for live STT tests

| File | Description |
|------|-------------|
| `sample.wav` | English speech, any duration, 16 kHz mono recommended |
| `sample.mp3` | Optional: same content in MP3 format |
| `sample.webm` | Optional: same content in WebM format |

## How to get free sample audio

### Option 1 — Record with Python (no extra tools)
```python
# Run from the voice-ai root:
import pyttsx3
engine = pyttsx3.init()
engine.save_to_file("Hello, this is a test of the speech recognition system.", "tests/sample_audio/sample.wav")
engine.runAndWait()
```

### Option 2 — Download a free sample
```bash
# Using curl (Linux/macOS/Windows Git Bash):
curl -L "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" -o tests/sample_audio/sample.mp3
```

### Option 3 — Use ffmpeg to generate a test tone
```bash
ffmpeg -f lavfi -i "sine=frequency=1000:duration=3" tests/sample_audio/sample.wav
```

### Option 4 — Record your own voice
Use any recording app (Windows Voice Recorder, macOS QuickTime, Audacity) and save as WAV.

## Without sample files

The STT live tests are automatically **skipped** when sample files are missing.
All error-handling and validation tests run without any audio files.
