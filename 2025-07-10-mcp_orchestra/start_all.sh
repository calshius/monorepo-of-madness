#!/bin/bash

# Start MCP Server
echo "Starting MCP Server..."
cd orchestra_instruments/src/orchestra_instruments
uvicorn api:app --host 0.0.0.0 --port 8000 --reload &
mcp_pid=$!
echo "MCP Server started with PID: $mcp_pid"
cd ../../../

# Start LLM API
echo "Starting LLM API..."
cd orchestra_instruments/src/llm_api
uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
llm_pid=$!
echo "LLM API started with PID: $llm_pid"
cd ../../../

# Start UI
echo "Starting UI..."
cd orchestra_ui
npm run dev &
ui_pid=$!
echo "UI started with PID: $ui_pid"
cd ../../

echo "All components started. MCP PID: $mcp_pid, LLM PID: $llm_pid, UI PID: $ui_pid"

