import io
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from orchestra_instruments.instruments import piano, violin

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

piano_agent = piano.Agent()
violin_agent = violin.Agent()

@app.get("/piano")
def play_piano():
    audio_buf = piano_agent.play_note("C4")  # Dummy note, as it's not used
    return StreamingResponse(audio_buf, media_type="audio/wav")

@app.get("/violin")
def play_violin():
    audio_buf = violin_agent.play_note("C4")  # Dummy note, as it's not used
    return StreamingResponse(audio_buf, media_type="audio/wav")

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }
