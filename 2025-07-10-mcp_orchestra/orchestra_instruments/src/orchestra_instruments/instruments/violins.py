import soundfile as sf
import io
import os

class Agent:
    def __init__(self):
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.wav_file = os.path.join(current_dir, "wav_files", "violins_1.wav")

    def play_note(self):
        data, samplerate = sf.read(self.wav_file)
        buf = io.BytesIO()
        sf.write(buf, data, samplerate, format='WAV')
        buf.seek(0)
        return buf
