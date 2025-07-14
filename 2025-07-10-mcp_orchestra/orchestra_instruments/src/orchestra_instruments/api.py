import io
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from orchestra_instruments.instruments import brass, woodwind, cellos, violins
import io
import soundfile as sf
import numpy as np
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

brass_agent = brass.Agent()
woodwind_agent = woodwind.Agent()
cellos_agent = cellos.Agent()
violins_agent = violins.Agent()

instrument_map = {
    "brass": brass_agent,
    "woodwind": woodwind_agent,
    "cellos": cellos_agent,
    "violins": violins_agent,
}

async def play_instrument(instrument_name: str):
    if instrument_name not in instrument_map:
        raise ValueError(f"Invalid instrument: {instrument_name}")
    agent = instrument_map[instrument_name]
    audio_buf = agent.play_note()
    data, samplerate = sf.read(audio_buf)
    return data, samplerate

@app.post("/play_instruments")
async def play_instruments(instruments: List[str]):
    """Plays the specified instruments simultaneously."""
    if not instruments:
        raise HTTPException(status_code=400, detail="No instruments specified")

    try:
        audio_data = []
        samplerates = []
        for instrument in instruments:
            data, samplerate = await play_instrument(instrument)
            audio_data.append(data)
            samplerates.append(samplerate)

        # Check if all samplerates are the same
        if len(set(samplerates)) > 1:
            raise ValueError("All audio files must have the same samplerate for mixing.")

        # Mix the audio data
        mixed_audio = np.sum(audio_data, axis=0)
        mixed_audio /= len(instruments)  # Normalize to prevent clipping

        # Convert to IO buffer
        buf = io.BytesIO()
        sf.write(buf, mixed_audio, samplerates[0], format='WAV')
        buf.seek(0)

        return Response(content=buf.read(), media_type="audio/wav")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
