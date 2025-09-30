from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Static
from .game_screen import GameScreen


class DungeonGameApp(App):
    """A Textual app for the Agentic Dungeon Escape game."""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #main-menu {
        align: center middle;
        width: auto;
        height: auto;
        padding: 2;
        border: thick $primary;
        background: $panel;
    }
    
    #title {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #subtitle {
        text-align: center;
        color: $text;
        margin-bottom: 2;
    }
    
    #game-area {
        align: center middle;
        width: 80%;
        height: auto;
        padding: 2;
        border: thick $primary;
        background: $panel;
    }
    
    #room-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    
    #room-description {
        text-align: center;
        margin-bottom: 1;
        padding: 1;
        background: $surface;
        border: solid $secondary;
    }
    
    #room-message {
        text-align: center;
        color: $warning;
        text-style: italic;
        margin-bottom: 2;
    }
    
    #navigation-grid {
        align: center middle;
        width: auto;
        height: auto;
    }
    
    #navigation-grid Button {
        margin: 1;
        min-width: 12;
    }
    
    #compass {
        text-align: center;
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Vertical(
            Static("🏰 AGENTIC DUNGEON ESCAPE 🏰", id="title"),
            Static("Welcome, brave adventurer!", id="subtitle"),
            Button.success("⚔️  Start Game", id="start-btn"),
            Button.error("🚪 Quit", id="quit-btn"),
            id="main-menu"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "start-btn":
            self.push_screen(GameScreen())
        elif event.button.id == "quit-btn":
            self.exit()


def main():
    """Run the Dungeon Game app."""
    app = DungeonGameApp()
    app.run()


if __name__ == "__main__":
    main()
