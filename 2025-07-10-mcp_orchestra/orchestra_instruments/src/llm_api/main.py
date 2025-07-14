from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import os
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

app = FastAPI()

gemini_api_key = os.getenv("GEMINI_TOKEN")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development - VERY IMPORTANT TO CHANGE FOR PRODUCTION)
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Explicitly allow OPTIONS
    allow_headers=["*"],  # Allows all headers
)


class LLMRequest(BaseModel):
    text: str


@app.post("/generate_music")
async def generate_music(request: LLMRequest):
    """Generates music based on the LLM's interpretation of the text input."""

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", google_api_key=gemini_api_key)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a music composition assistant.  You receive text requests from the user and translate them into instructions for an orchestra.  You can request the following instruments: brass, woodwind, cellos, violins.

        Your response MUST be a valid JSON list of strings, representing the instruments to play. Do not include any other text, markdown, or formatting.

        Example Response:
        ["violins", "cellos", "brass"]

        If the user asks for something that is not related to the available instruments, respond with an empty list: `[]`
         
        Do not return any markdown formatting or anything that has backticks like this:
         
        ```json
         ["violins", "cellos", "brass"]
        ```
        """),
        ("user", "{text}")
    ])

    chain = prompt | llm

    try:
        llm_response = await chain.ainvoke({"text": request.text})
        instruments_string = llm_response.content
        print(f"LLM Response: {instruments_string}")

        # Parse the JSON string
        try:
            instruments = json.loads(instruments_string)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Invalid JSON from LLM: {e}.  Raw response: {instruments_string}")

        # Call the MCP server
        mcp_server_url = "http://127.0.0.1:8000/play_instruments"  # Replace with your MCP server URL
        response = requests.post(mcp_server_url, json=instruments)
        response.raise_for_status()
        return Response(content=response.content, media_type="audio/wav")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling MCP server: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
