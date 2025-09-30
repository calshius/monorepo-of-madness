from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Static


class DungeonGameApp(App):
    """A Textual app for the Agentic Dungeon Escape game."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Vertical(
            Static("🏰 AGENTIC DUNGEON ESCAPE 🏰"),
            Static("Welcome, brave adventurer!"),
            Button.success("⚔️  Start Game", id="start-btn"),
            Button.error("🚪 Quit", id="quit-btn"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "start-btn":
            self.notify("Game starting... (Coming soon!)")
        elif event.button.id == "quit-btn":
            self.exit()


def main():
    """Run the Dungeon Game app."""
    app = DungeonGameApp()
    app.run()


if __name__ == "__main__":
    main()
