#!/bin/bash

# Stop MCP Server
echo "Stopping MCP Server..."
if [ -n "$mcp_pid" ]; then
  kill "$mcp_pid"
  echo "MCP Server stopped (PID: $mcp_pid)"
else
  echo "MCP Server PID not found. Trying to kill process on port 8000..."
  kill $(lsof -t -i:8000) || true
fi

# Stop LLM API
echo "Stopping LLM API..."
if [ -n "$llm_pid" ]; then
  kill "$llm_pid"
  echo "LLM API stopped (PID: $llm_pid)"
else
  echo "LLM API PID not found. Trying to kill process on port 8001..."
  kill $(lsof -t -i:8001) || true
fi

# Stop UI
echo "Stopping UI..."
if [ -n "$ui_pid" ]; then
  kill "$ui_pid"
  echo "UI stopped (PID: $ui_pid)"
else
  echo "UI PID not found. Trying to kill process on port 5173..."
  kill $(lsof -t -i:5173) || true
fi

echo "All components stopped."
