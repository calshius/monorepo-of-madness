"""
Start screen for the AI Dungeon game.
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static, Button
from textual.screen import Screen


class StartScreen(Screen):
    """Welcome screen for the AI Dungeon game."""
    
    CSS = """
    StartScreen {
        align: center middle;
    }
    
    #welcome_container {
        width: 60;
        height: 20;
        border: solid cyan;
        padding: 2;
    }
    
    #title {
        text-align: center;
        color: cyan;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #subtitle {
        text-align: center;
        color: white;
        margin-bottom: 2;
    }
    
    #description {
        text-align: center;
        color: gray;
        margin-bottom: 2;
    }
    
    Button {
        width: 100%;
        margin: 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Compose the start screen layout."""
        with Container(id="welcome_container"):
            with Vertical():
                yield Static("🏰 AI DUNGEON 🏰", id="title")
                yield Static("Text Adventure Game", id="subtitle")
                yield Static(
                    "Welcome, brave adventurer!\n"
                    "Embark on an epic journey through a world of magic and mystery.\n"
                    "Your choices shape the story!",
                    id="description"
                )
                yield Button("🎮 Start New Game", id="new_game", variant="primary")
                yield Button("❌ Quit", id="quit", variant="error")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "new_game":
            # Switch to the game screen
            self.app.push_screen("game")
        elif event.button.id == "quit":
            self.app.exit()
