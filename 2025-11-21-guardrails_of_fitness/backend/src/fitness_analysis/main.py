"""FastAPI application with WebSocket support for fitness analysis."""

import os
import json
from typing import AsyncGenerator
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from .agent_enhanced import get_fitness_agent

# Load environment variables from .env file (won't override existing env vars)
load_dotenv()

# Check for GEMINI_TOKEN in environment variables first, then .env file
gemini_token = os.getenv("GEMINI_TOKEN")
if not gemini_token:
    raise ValueError("GEMINI_TOKEN environment variable is required. Set it as an environment variable or in backend/.env file")

# Set GOOGLE_API_KEY from GEMINI_TOKEN for langchain compatibility
os.environ["GOOGLE_API_KEY"] = gemini_token

# Create FastAPI app
app = FastAPI(title="Fitness Analysis API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],  # Vite dev and preview
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Fitness Analysis API", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming agent responses."""
    await websocket.accept()
    
    # Create a unique thread ID for this session
    thread_id = f"thread_{id(websocket)}"
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            if not user_message:
                await websocket.send_json({
                    "type": "error",
                    "content": "Empty message received"
                })
                continue
            
            # Get the agent
            agent = get_fitness_agent()
            
            # Create input state
            input_state = {
                "messages": [HumanMessage(content=user_message)]
            }
            
            # Stream the agent's response
            try:
                # Send start signal
                await websocket.send_json({
                    "type": "start",
                    "content": "Processing your request..."
                })
                
                # Stream events from the agent
                async for event in agent.astream_events(input_state, config, version="v2"):
                    kind = event.get("event")
                    
                    # Handle different event types
                    if kind == "on_chat_model_stream":
                        # Stream LLM tokens
                        chunk = event.get("data", {}).get("chunk")
                        if chunk and hasattr(chunk, "content"):
                            if chunk.content:
                                await websocket.send_json({
                                    "type": "token",
                                    "content": chunk.content
                                })
                    
                    elif kind == "on_tool_start":
                        # Tool is being called
                        tool_name = event.get("name", "unknown")
                        await websocket.send_json({
                            "type": "tool_start",
                            "content": f"Using tool: {tool_name}"
                        })
                    
                    elif kind == "on_tool_end":
                        # Tool finished
                        tool_name = event.get("name", "unknown")
                        await websocket.send_json({
                            "type": "tool_end",
                            "content": f"Finished: {tool_name}"
                        })
                
                # Send completion signal
                await websocket.send_json({
                    "type": "end",
                    "content": "Response complete"
                })
                
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "content": f"Error processing request: {str(e)}"
                })
    
    except WebSocketDisconnect:
        print(f"Client disconnected: {thread_id}")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "content": f"Server error: {str(e)}"
            })
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
