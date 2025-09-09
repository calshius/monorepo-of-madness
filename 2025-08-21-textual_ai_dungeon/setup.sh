#!/bin/bash

echo "🏰 Setting up AI Dungeon..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Install dependencies and create virtual environment
echo "Installing dependencies with uv..."
uv sync

echo "✅ Setup complete!"
echo ""
echo "To run the game:"
echo "1. Set your Google API key: export GOOGLE_API_KEY='your-key-here'"
echo "2. Run the game: uv run python -m ai_dungeon.main"
echo ""
echo "Additional options:"
echo "- Run without AI: uv run python -m ai_dungeon.main --no-ai"
echo "- Debug mode: uv run python -m ai_dungeon.main --debug"
echo ""
echo "Note: After installation, you can also try: uv run start-dungeon-game"
