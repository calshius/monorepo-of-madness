#!/usr/bin/env python3
"""
Simple test script to verify the game components work correctly.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_game_components():
    """Test the core game components."""
    print("Testing AI Dungeon components...")
    
    try:
        # Test imports
        from ai_dungeon.core.engine import GameEngine
        from ai_dungeon.core.models import GameState
        from ai_dungeon.player.player import Player
        from ai_dungeon.world.world import World
        print("✅ All core imports successful")
        
        # Test basic initialization
        engine = GameEngine(None)  # No API key for testing
        print("✅ Game engine initialized")
        
        # Test world creation
        world = World()
        print("✅ World created with initial locations")
        print(f"   - Locations: {list(world.locations.keys())}")
        print(f"   - Items: {list(world.items.keys())}")
        print(f"   - NPCs: {list(world.npcs.keys())}")
        
        # Test player
        player = Player()
        print("✅ Player created")
        print(f"   - Name: {player.name}")
        print(f"   - Level: {player.level}")
        print(f"   - Stats: STR:{player.stats.strength}, DEX:{player.stats.dexterity}")
        
        # Test location description
        desc = engine.get_current_location_description()
        print("✅ Location description generated")
        print(f"   - Description length: {len(desc)} characters")
        
        # Test command parsing
        from ai_dungeon.core.utils import CommandParser
        parser = CommandParser()
        
        test_commands = ["north", "look", "take key", "inventory", "help"]
        for cmd in test_commands:
            parsed = parser.parse_command(cmd)
            print(f"   - '{cmd}' -> {parsed.command_type.value}: {parsed.action}")
        
        print("\n🎮 All tests passed! The game should work correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_game_components()
    sys.exit(0 if success else 1)
