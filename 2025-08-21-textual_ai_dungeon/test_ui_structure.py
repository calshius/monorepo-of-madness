#!/usr/bin/env python3
"""
Test the simplified UI structure.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ui_structure():
    """Test the new modular UI structure."""
    print("Testing simplified UI structure...")
    
    try:
        # Test imports
        from ai_dungeon.ui.app import DungeonApp
        from ai_dungeon.ui.start_screen import StartScreen
        from ai_dungeon.ui.game_screen import GameScreen
        from ai_dungeon.ui.utils import format_text_for_display, style_text, get_text_style
        print("✅ All UI module imports successful")
        
        # Test text utilities
        test_text = "This is a very long line that should be wrapped to test the formatting function because it exceeds the maximum width."
        formatted = format_text_for_display(test_text, 40)
        print(f"✅ Text formatting works: {len(formatted.split('\\n'))} lines")
        
        # Test styling
        styled = style_text("Test message", "success")
        print(f"✅ Text styling works: {styled}")
        
        # Test auto-styling
        error_style = get_text_style("Error: something went wrong")
        success_style = get_text_style("You gained 10 experience!")
        print(f"✅ Auto-styling works: error='{error_style}', success='{success_style}'")
        
        # Test app creation (without running)
        app = DungeonApp(api_key=None)
        print("✅ App creation successful")
        
        print("\\n🎉 All UI structure tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during UI testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ui_structure()
    if success:
        print("\\n🚀 Ready to launch: python -m ai_dungeon.main --no-ai")
    sys.exit(0 if success else 1)
