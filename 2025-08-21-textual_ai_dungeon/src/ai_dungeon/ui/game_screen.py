"""
Game screen for the AI Dungeon.
"""

import asyncio
from typing import Optional
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.widgets import Static, Input, Button
from textual.screen import Screen

from ai_dungeon.core.engine import GameEngine


class GameScreen(Screen):
    """Main game screen for playing the AI Dungeon."""
    
    CSS = """
    #main_container {
        layout: vertical;
    }
    
    #game_output {
        height: 1fr;
        border: solid white;
        padding: 1;
    }
    
    #status_bar {
        height: 3;
        border: solid cyan;
        padding: 1;
    }
    
    #input_container {
        height: 3;
        border: solid green;
        padding: 1;
    }
    
    #command_input {
        width: 1fr;
    }
    
    .error {
        color: red;
    }
    
    .success {
        color: green;
    }
    
    .ai_response {
        color: blue;
    }
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the game screen."""
        super().__init__()
        self.game_engine = GameEngine(api_key)
        self.command_history = []
        self.history_index = -1
    
    def compose(self) -> ComposeResult:
        """Compose the game screen layout."""
        with Container(id="main_container"):
            # Game output area
            with ScrollableContainer(id="game_output"):
                yield Static("", id="output_display")
            
            # Status bar
            with Container(id="status_bar"):
                with Horizontal():
                    yield Static("Starting...", id="player_status")
                    yield Static("Unknown Location", id="location_status")
                    yield Static("Turn: 0", id="game_stats")
            
            # Input area
            with Container(id="input_container"):
                with Horizontal():
                    yield Input(placeholder="Enter your command...", id="command_input")
                    yield Button("Send", id="send_button", variant="primary")
    
    def on_mount(self) -> None:
        """Initialize the game when the screen loads."""
        self.query_one("#command_input").focus()
        asyncio.create_task(self._start_new_game())
    
    async def _start_new_game(self) -> None:
        """Start a new game and show the welcome message."""
        try:
            self._add_output("🏰 Welcome to your Adventure! 🏰")
            self._add_output("=" * 50)
            self._add_output("")
            self._add_output("🎮 NEW GAME STARTED! 🎮")
            self._add_output("")
            self._add_output("You are an adventurer who has just awakened in a mysterious place.")
            self._add_output("Your memories are hazy, but your spirit of adventure burns bright!")
            self._add_output("")
            self._add_output("Type 'help' for commands, or start exploring!")
            self._add_output("Try: 'look', 'north', 'take key', 'inventory'")
            self._add_output("")
            
            # Initialize game state
            self.game_engine.game_state.current_location = "starting_room"
            if "starting_room" not in self.game_engine.game_state.visited_locations:
                self.game_engine.game_state.visited_locations.append("starting_room")
            
            # Show initial location
            description = self.game_engine.get_current_location_description()
            self._add_output(description)
            
            self._update_status()
            
        except Exception as e:
            self._add_output(f"Error starting game: {str(e)}", "error")
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command input."""
        await self._process_command(event.value)
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "send_button":
            command_input = self.query_one("#command_input")
            await self._process_command(command_input.value)
    
    async def _process_command(self, command: str) -> None:
        """Process a player command."""
        command = command.strip()
        if not command:
            return
        
        # Clear input
        command_input = self.query_one("#command_input")
        command_input.value = ""
        
        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Show command
        self._add_output(f"\n> {command}")
        
        try:
            # Process command
            result = await self.game_engine.process_command(command)
            
            if result == "QUIT_GAME":
                self.app.pop_screen()
                return
            
            # Show result with appropriate styling
            if "error" in result.lower() or "cannot" in result.lower():
                self._add_output(result, "error")
            elif "gained" in result.lower() or "level up" in result.lower():
                self._add_output(result, "success")
            elif "says:" in result or "dialogue" in result.lower():
                self._add_output(result, "ai_response")
            else:
                self._add_output(result)
            
            self._update_status()
            
        except Exception as e:
            self._add_output(f"Error processing command: {str(e)}", "error")
    
    def _add_output(self, text: str, style: str = "") -> None:
        """Add text to the output display."""
        if not text:
            return
        
        # Simple text formatting
        formatted_text = text
        if style:
            formatted_text = f"[{style}]{text}[/{style}]"
        
        # Update output
        current_output = self.query_one("#output_display").renderable
        if isinstance(current_output, str):
            new_output = current_output + "\n" + formatted_text
        else:
            new_output = str(current_output) + "\n" + formatted_text
        
        self.query_one("#output_display").update(new_output)
        
        # Scroll to bottom
        self.query_one("#game_output").scroll_end()
    
    def _update_status(self) -> None:
        """Update the status bar with current game information."""
        try:
            # Player info
            player = self.game_engine.player
            player_text = f"❤️  Level: {player.level} | STR: {player.stats.strength}"
            if player.experience > 0:
                player_text += f" | XP: {player.experience}"
            
            self.query_one("#player_status").update(player_text)
            
            # Location info
            current_location = self.game_engine.world.get_location(
                self.game_engine.game_state.current_location
            )
            location_name = current_location.name if current_location else "Unknown"
            location_text = f"📍 {location_name.replace('_', ' ').title()}"
            
            self.query_one("#location_status").update(location_text)
            
            # Game stats
            stats = self.game_engine.get_game_stats()
            stats_text = f"🎮 Turn: {stats['turns']} | Score: {stats['score']}"
            
            self.query_one("#game_stats").update(stats_text)
            
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def on_key(self, event) -> None:
        """Handle key presses for command history."""
        if event.key == "escape":
            self.app.pop_screen()
        elif event.key == "up" and self.command_history:
            if self.history_index > 0:
                self.history_index -= 1
                command_input = self.query_one("#command_input")
                command_input.value = self.command_history[self.history_index]
        elif event.key == "down" and self.command_history:
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                command_input = self.query_one("#command_input")
                command_input.value = self.command_history[self.history_index]
            else:
                command_input = self.query_one("#command_input")
                command_input.value = ""
                self.history_index = len(self.command_history)
