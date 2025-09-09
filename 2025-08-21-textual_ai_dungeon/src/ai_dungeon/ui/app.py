"""
Main application for the AI Dungeon game.
"""

from typing import Optional
from textual.app import App
from textual.binding import Binding

from ai_dungeon.ui.start_screen import StartScreen
from ai_dungeon.ui.game_screen import GameScreen


class DungeonApp(App):
    """Main application for the AI Dungeon game."""
    
    TITLE = "AI Dungeon - Text Adventure"
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the application."""
        super().__init__()
        self.api_key = api_key
    
    def on_mount(self) -> None:
        """Set up the application when it starts."""
        # Install screens
        self.install_screen(StartScreen(), name="start")
        self.install_screen(GameScreen(self.api_key), name="game")
        
        # Start with the start screen
        self.push_screen("start")


def main(api_key: Optional[str] = None):
    """Main entry point for the game."""
    app = DungeonApp(api_key)
    app.run()


if __name__ == "__main__":
    import os
    api_key = os.getenv("GOOGLE_API_KEY")
    main(api_key)