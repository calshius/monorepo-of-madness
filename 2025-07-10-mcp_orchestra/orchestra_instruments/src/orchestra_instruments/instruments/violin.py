import io
import os
from pydub import AudioSegment

MP3_PATH = "/home/callum/projects/monorepo-of-madness/2025-07-10-mcp_orchestra/orchestra_instruments/src/orchestra_instruments/instruments/mp3/violin.mp3"
CLIP_DURATION_MS = 10000  # 10 seconds
START_TIME_MS = 3000  # Start at 3 seconds (in milliseconds)

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

        # Extract the clip starting at START_TIME_MS
        start_clip = self.audio[START_TIME_MS:]

        # Get the first CLIP_DURATION_MS milliseconds of the extracted clip
        clip = start_clip[:CLIP_DURATION_MS]

        # Speed up the clip by 20%
        playback_speed = 1.2  # 1.0 = normal speed, 1.2 = 20% faster
        sped_up = clip.speedup(playback_speed=playback_speed)

        # Convert to WAV format in memory
        wav_io = io.BytesIO()
        sped_up.export(wav_io, format="wav")
        wav_io.seek(0)
        return wav_io

    def status(self):
        return "ready" if self.audio else "not_initialized"
