#!/usr/bin/env python3
"""
AI Dungeon - An immersive text-based adventure game.

A dynamic text adventure powered by LangGraph and Google Gemini AI
for intelligent world generation and engaging dialogue.

Usage:
    python -m ai_dungeon.main
    
Environment Variables:
    GOOGLE_API_KEY: Your Google Gemini API key for AI features
"""

import os
import sys
import argparse

try:
    from ai_dungeon.ui.app import main as run_ui
except ImportError:
    # Fallback if UI imports fail
    print("Warning: Could not import UI modules. Some dependencies may be missing.")
    run_ui = None


def main():
    """Main entry point for the AI Dungeon game."""
    parser = argparse.ArgumentParser(description="AI-Powered Text Adventure Game")
    parser.add_argument(
        "--api-key", 
        help="Google Gemini API key (can also be set via GOOGLE_API_KEY env var)"
    )
    parser.add_argument(
        "--no-ai", 
        action="store_true", 
        help="Run without AI features (uses fallback content)"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Set up API key
    api_key = args.api_key or os.getenv("GOOGLE_API_KEY")
    
    if not api_key and not args.no_ai:
        print("Warning: No Google API key provided. AI features will be limited.")
        print("Set GOOGLE_API_KEY environment variable or use --api-key option.")
        print("Use --no-ai flag to run without AI features.")
        print()
    
    if args.debug:
        print(f"Debug mode enabled")
        print(f"API key provided: {'Yes' if api_key else 'No'}")
        print(f"AI disabled: {args.no_ai}")
        print()
    
    # Check dependencies
    missing_deps = []
    
    try:
        import textual
    except ImportError:
        missing_deps.append("textual")
    
    if not args.no_ai:
        try:
            import langchain_google_genai
        except ImportError:
            missing_deps.append("langchain-google-genai")
        
        try:
            import langgraph
        except ImportError:
            missing_deps.append("langgraph")
    
    if missing_deps:
        print("Missing required dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nInstall with: pip install " + " ".join(missing_deps))
        sys.exit(1)
    
    # Launch the game
    try:
        if run_ui:
            print("🏰 Starting AI Dungeon...")
            print("Press Ctrl+C to quit")
            print()
            run_ui(api_key if not args.no_ai else None)
        else:
            print("Error: Could not start the game UI.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error starting game: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()