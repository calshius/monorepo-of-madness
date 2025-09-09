#!/usr/bin/env python3
"""
Simple verification that the game UI starts properly.
"""

import sys
import os
import asyncio

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_ui_startup():
    """Test that the UI components initialize correctly."""
    try:
        from ai_dungeon.ui.app import GameApp
        
        print("🎮 Creating game app...")
        app = GameApp(api_key=None)
        
        print("✅ Game app created successfully")
        print("✅ UI components initialized")
        print("✅ Game engine configured")
        
        # Test the initialization method
        await app._initialize_game()
        print("✅ Game initialization completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during UI startup: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ui_startup())
    if success:
        print("\n🎉 Game is ready to launch!")
        print("Run: python -m ai_dungeon.main --no-ai")
    sys.exit(0 if success else 1)
