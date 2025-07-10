import io
import os
from pydub import AudioSegment

MP3_PATH = "/home/callum/projects/monorepo-of-madness/2025-07-10-mcp_orchestra/orchestra_instruments/src/orchestra_instruments/instruments/mp3/paino.mp3"
CLIP_DURATION_MS = 10000  # 10 seconds

class Agent:
    def __init__(self):
        try:
            self.audio = AudioSegment.from_mp3(MP3_PATH)
        except Exception as e:
            print(f"Error loading MP3: {e}")
            self.audio = None

    def play_note(self, note: str):
        if self.audio is None:
            return io.BytesIO()

        # Get the first CLIP_DURATION_MS milliseconds
        clip = self.audio[:CLIP_DURATION_MS]

        # Convert to WAV format in memory
        wav_io = io.BytesIO()
        clip.export(wav_io, format="wav")
        wav_io.seek(0)
        return wav_io

    def status(self):
        return "ready" if self.audio else "not_initialized"
