"""
Main game engine that orchestrates all game systems.

This module provides the central GameEngine class that coordinates
the world, player, AI, and UI systems.
"""

from typing import Dict, Optional, Any
import json
from dataclasses import asdict

# Import our modules
from ai_dungeon.core.models import GameState, GameCommand, CommandType, Location, NPC
from ai_dungeon.core.utils import CommandParser
from ai_dungeon.player.player import Player
from ai_dungeon.world.world import World
from ai_dungeon.ai.gemini_engine import GeminiAIEngine, WorldGenerationRequest


class GameEngine:
    """Main game engine that orchestrates all game systems."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the game engine."""
        self.game_state = GameState()
        self.player = Player()
        self.world = World()
        self.ai_engine = GeminiAIEngine(api_key)
        self.command_parser = CommandParser()
        
        # Game statistics
        self.commands_processed = 0
        self.locations_generated = 0
    
    async def process_command(self, raw_command: str) -> str:
        """Process a player command and return the result."""
        self.commands_processed += 1
        self.game_state.turn_count += 1
        
        # Parse the command
        command = self.command_parser.parse_command(raw_command)
        
        # Process the command based on type
        try:
            if command.command_type == CommandType.MOVEMENT:
                result = await self._handle_movement(command)
            elif command.command_type == CommandType.INVENTORY:
                result = self._handle_inventory(command)
            elif command.command_type == CommandType.INTERACTION:
                result = await self._handle_interaction(command)
            elif command.command_type == CommandType.DIALOGUE:
                result = await self._handle_dialogue(command)
            elif command.command_type == CommandType.SYSTEM:
                result = self._handle_system(command)
            else:
                result = await self._handle_unknown_command(command)
            
            # Process any turn-based effects
            turn_effects = self.player.process_turn()
            if turn_effects:
                result += "\n\n" + turn_effects
            
            return result
            
        except Exception as e:
            return f"An error occurred while processing your command: {str(e)}"
    
    async def _handle_movement(self, command: GameCommand) -> str:
        """Handle movement commands."""
        current_location = self.world.get_location(self.game_state.current_location)
        if not current_location:
            return "You seem to be lost in space and time."
        
        direction = command.target
        if not direction:
            return "Which direction do you want to go?"
        
        # Check if direction is valid from current location
        if direction not in current_location.exits:
            return f"You cannot go {direction} from here."
        
        destination_name = current_location.exits[direction]
        destination = self.world.get_location(destination_name)
        
        # If destination doesn't exist, generate it using AI
        if not destination:
            destination = await self._generate_location(destination_name, direction)
            if destination:
                self.world.add_location(destination)
                self.locations_generated += 1
            else:
                return f"The path {direction} seems to be blocked."
        
        # Check if this is the first visit
        first_visit = destination_name not in self.game_state.visited_locations
        
        # Move the player
        self.game_state.current_location = destination_name
        if first_visit:
            self.game_state.visited_locations.append(destination_name)
            # Gain experience for discovering new locations
            self.player.gain_experience(10)
        
        # Return location description
        return self.world.get_location_description(destination_name, first_visit)
    
    def _handle_inventory(self, command: GameCommand) -> str:
        """Handle inventory-related commands."""
        action = command.action
        target = command.target
        
        if action == "show_inventory":
            return self.player.inventory.get_inventory_display()
        
        elif action in ["take", "get", "pick_up", "grab"]:
            if not target:
                return "Take what?"
            
            # Check if item exists in current location
            current_location = self.world.get_location(self.game_state.current_location)
            if not current_location:
                return "You are nowhere."
            
            # Find the item
            item_template = None
            item_key = None
            for item_name in current_location.items:
                item = self.world.get_item(item_name)
                if item and (target.lower() in item.name.lower() or item.name.lower() in target.lower()):
                    item_template = item
                    item_key = item_name
                    break
            
            if not item_template:
                return f"There is no {target} here."
            
            # Try to add to inventory
            if self.player.inventory.add_item(item_template):
                current_location.items.remove(item_key)
                return f"You take the {item_template.name}."
            else:
                return f"You cannot carry the {item_template.name}. Your inventory is full or too heavy."
        
        elif action in ["drop", "put_down", "leave"]:
            if not target:
                return "Drop what?"
            
            item = self.player.inventory.remove_item(target)
            if item:
                # Add item back to current location
                current_location = self.world.get_location(self.game_state.current_location)
                if current_location:
                    # Add to world registry if not already there
                    item_key = target.lower().replace(" ", "_")
                    self.world.items[item_key] = item
                    current_location.items.append(item_key)
                return f"You drop the {item.name}."
            else:
                return f"You don't have a {target}."
        
        elif action in ["use", "consume", "eat", "drink"]:
            if not target:
                return "Use what?"
            
            result = self.player.inventory.use_item(target)
            return result or f"You cannot use the {target}."
        
        return "I don't understand that inventory command."
    
    async def _handle_interaction(self, command: GameCommand) -> str:
        """Handle interaction commands."""
        action = command.action
        target = command.target
        
        if action == "look_around":
            return self.world.get_location_description(self.game_state.current_location)
        
        elif action in ["look", "examine", "inspect", "check"]:
            if not target:
                return "Examine what?"
            
            # Check if target is an item in inventory
            item = self.player.inventory.get_item(target)
            if item:
                return f"The {item.name}: {item.description}"
            
            # Check if target is an item in current location
            current_location = self.world.get_location(self.game_state.current_location)
            if current_location:
                for item_name in current_location.items:
                    item = self.world.get_item(item_name)
                    if item and (target.lower() in item.name.lower() or item.name.lower() in target.lower()):
                        return f"The {item.name}: {item.description}"
            
            # Check if target is an NPC
            npc = self.world.get_npc(target)
            if npc:
                return f"{npc.name}: {npc.description}"
            
            # Use AI to generate examination description
            context = {
                "action": f"examine {target}",
                "location": self.game_state.current_location,
                "player_inventory": [item.name for item in self.player.inventory.list_items()],
                "game_state": asdict(self.game_state)
            }
            
            request = WorldGenerationRequest(
                task_type="description",
                context=context,
                parameters={}
            )
            
            return await self.ai_engine.generate_content(request)
        
        elif action in ["talk_to", "speak_to", "talk_with", "speak_with"]:
            return await self._handle_dialogue_with_target(target)
        
        elif action in ["attack", "fight", "hit", "strike"]:
            return await self._handle_combat(target)
        
        return f"I don't know how to {action} {target}."
    
    async def _handle_combat(self, target: str) -> str:
        """Handle combat with enemies."""
        if not target:
            return "Attack what?"
        
        # Check if target is an NPC that can be fought
        npc = self.world.get_npc(target)
        if not npc:
            return f"There is no {target} here to fight."
        
        # Check if NPC is hostile or can be fought
        if npc.disposition == "friendly":
            return f"The {npc.name} doesn't seem hostile. You might try talking to them instead."
        
        # Generate combat encounter using AI
        context = {
            "action": f"attack {target}",
            "enemy_name": npc.name,
            "enemy_description": npc.description,
            "player_level": self.player.level,
            "player_stats": asdict(self.player.stats),
            "location": self.game_state.current_location,
            "game_state": asdict(self.game_state)
        }
        
        request = WorldGenerationRequest(
            task_type="combat",
            context=context,
            parameters={"enemy": npc.name}
        )
        
        combat_result = await self.ai_engine.generate_content(request)
        
        # Apply combat results
        if "victory" in combat_result.lower() or "defeat" in combat_result.lower():
            # Gain experience for combat
            exp_gained = max(5 * self.player.level, 10)
            self.player.gain_experience(exp_gained)
            combat_result += f"\n\nYou gain {exp_gained} experience points!"
            
            # Check for level up
            if self.player.can_level_up():
                level_message = self.player.level_up()
                combat_result += f"\n{level_message}"
        
        return combat_result
    
    async def _handle_dialogue(self, command: GameCommand) -> str:
        """Handle dialogue commands."""
        # Find NPCs in current location
        current_location = self.world.get_location(self.game_state.current_location)
        if not current_location or not current_location.npcs:
            return "There's no one here to talk to."
        
        # If multiple NPCs, talk to the first one
        npc_key = current_location.npcs[0]
        npc = self.world.get_npc(npc_key)
        if not npc:
            return "The character seems to have vanished."
        
        return await self._generate_dialogue(npc, command.target or "hello")
    
    async def _handle_dialogue_with_target(self, target: str) -> str:
        """Handle dialogue with a specific target."""
        if not target:
            return "Talk to whom?"
        
        npc = self.world.get_npc(target)
        if not npc:
            return f"There is no {target} here to talk to."
        
        return await self._generate_dialogue(npc, "hello")
    
    def _handle_system(self, command: GameCommand) -> str:
        """Handle system commands."""
        action = command.action
        
        if action == "help":
            return """
Available commands:
• Movement: north, south, east, west (or n, s, e, w), up, down
• Inventory: inventory, take [item], drop [item], use [item]
• Interaction: look, examine [item], talk to [character]
• System: help, quit, status, save, load

Special features:
• Dynamic world generation - new areas are created as you explore!
• AI-powered NPCs with dynamic dialogue
• Character progression with stats and leveling
• Rich inventory system with item properties

Type 'status' to see your character information.
            """.strip()
        
        elif action == "quit":
            return "QUIT_GAME"  # Special signal for the UI
        
        elif action in ["status", "stats"]:
            return self.player.get_character_sheet()
        
        elif action == "save":
            return self._save_game()
        
        elif action == "load":
            return self._load_game()
        
        return f"System command '{action}' not implemented yet."
    
    async def _handle_unknown_command(self, command: GameCommand) -> str:
        """Handle unknown commands using AI."""
        context = {
            "command": command.raw_command,
            "location": self.game_state.current_location,
            "player_inventory": [item.name for item in self.player.inventory.list_items()],
            "game_state": asdict(self.game_state)
        }
        
        request = WorldGenerationRequest(
            task_type="description",
            context=context,
            parameters={}
        )
        
        return await self.ai_engine.generate_content(request)
    
    async def _generate_location(self, location_name: str, direction: str) -> Optional[Location]:
        """Generate a new location using AI."""
        context = {
            "current_location": self.game_state.current_location,
            "direction": direction,
            "game_state": asdict(self.game_state),
            "visited_locations": self.game_state.visited_locations
        }
        
        request = WorldGenerationRequest(
            task_type="location",
            context=context,
            parameters={"name": location_name}
        )
        
        try:
            result = await self.ai_engine.generate_content(request)
            location_data = json.loads(result)
            
            # Ensure the location name matches what we expect
            location_data["name"] = location_name
            location_data["generated_by_ai"] = True
            
            return Location.from_dict(location_data)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing generated location: {e}")
            # Create a basic fallback location
            return Location(
                name=location_name,
                description=f"You find yourself in {location_name.replace('_', ' ')}. The area is mysterious and unexplored.",
                exits={},
                items=[],
                npcs=[],
                generated_by_ai=False
            )
        except Exception as e:
            print(f"Error generating location: {e}")
            return None
    
    async def _generate_dialogue(self, npc: NPC, player_input: str) -> str:
        """Generate dialogue for an NPC."""
        context = {
            "npc_name": npc.name,
            "player_action": player_input,
            "dialogue_history": npc.dialogue_history,
            "disposition": npc.disposition,
            "location": self.game_state.current_location,
            "game_state": asdict(self.game_state)
        }
        
        request = WorldGenerationRequest(
            task_type="dialogue",
            context=context,
            parameters={}
        )
        
        dialogue = await self.ai_engine.generate_content(request)
        
        # Update NPC dialogue history
        npc.dialogue_history.append(f"Player: {player_input}")
        npc.dialogue_history.append(f"{npc.name}: {dialogue}")
        
        return f"{npc.name} says: \"{dialogue}\""
    
    def _save_game(self) -> str:
        """Save the current game state."""
        try:
            save_data = {
                "game_state": self.game_state.to_dict(),
                "player": self.player.to_dict(),
                "world": self.world.to_dict()
            }
            
            with open("savegame.json", "w") as f:
                json.dump(save_data, f, indent=2)
            
            return "Game saved successfully!"
        except Exception as e:
            return f"Failed to save game: {str(e)}"
    
    def _load_game(self) -> str:
        """Load a saved game state."""
        try:
            with open("savegame.json", "r") as f:
                save_data = json.load(f)
            
            self.game_state = GameState.from_dict(save_data["game_state"])
            self.player = Player.from_dict(save_data["player"])
            self.world = World.from_dict(save_data["world"])
            
            return "Game loaded successfully!"
        except FileNotFoundError:
            return "No saved game found."
        except Exception as e:
            return f"Failed to load game: {str(e)}"
    
    def get_current_location_description(self) -> str:
        """Get the description of the current location."""
        return self.world.get_location_description(self.game_state.current_location)
    
    def get_game_stats(self) -> Dict[str, Any]:
        """Get game statistics."""
        return {
            "commands_processed": self.commands_processed,
            "locations_generated": self.locations_generated,
            "turns": self.game_state.turn_count,
            "score": self.game_state.score,
            "locations_visited": len(self.game_state.visited_locations),
            "player_level": self.player.level
        }
