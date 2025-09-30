from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static, Header, Footer
from .rooms.enemy import EnemyRoom
from .rooms.merchant import MerchantRoom
from .rooms.road import RoadRoom
from .rooms.wizard import WizardRoom
import random


class GameScreen(Screen):
    """The main game screen with room display and navigation."""
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Back to Menu"),
    ]
    
    def __init__(self):
        super().__init__()
        self.current_room = None
        self.room_types = [EnemyRoom, MerchantRoom, RoadRoom, WizardRoom]
        self.enter_starting_room()
    
    def compose(self) -> ComposeResult:
        """Create the game interface."""
        yield Header()
        yield Vertical(
            Static("", id="room-title"),
            Static("", id="room-description"),
            Static("", id="room-message"),
            Vertical(
                Button("⬆️ North", id="north", variant="primary"),
                Horizontal(
                    Button("⬅️ West", id="west", variant="primary"),
                    Static("   🧭   ", id="compass"),
                    Button("➡️ East", id="east", variant="primary"),
                ),
                Button("⬇️ South", id="south", variant="primary"),
                id="navigation-grid"
            ),
            id="game-area"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        self.update_room_display()
    
    def enter_starting_room(self) -> None:
        """Enter the initial room (always a road for a gentle start)."""
        self.current_room = RoadRoom()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle navigation button presses."""
        if event.button.id in ["north", "east", "south", "west"]:
            self.move_to_new_room(event.button.id)
    
    def move_to_new_room(self, direction: str) -> None:
        """Move to a randomly selected new room."""
        # Randomly select a room type
        room_class = random.choice(self.room_types)
        self.current_room = room_class()
        
        # Show entrance message briefly
        entrance_message = self.current_room.enter()
        self.query_one("#room-message").update(f"Going {direction}... {entrance_message}")
        
        # Update the room display
        self.update_room_display()
        
        # Clear the message after 3 seconds
        self.set_timer(3.0, self.clear_message)
    
    def update_room_display(self) -> None:
        """Update the display with current room information."""
        if self.current_room:
            room_info = self.current_room.get_display_info()
            
            title_text = f"{room_info['emoji']} {room_info['name']} {room_info['emoji']}"
            self.query_one("#room-title").update(title_text)
            
            self.query_one("#room-description").update(room_info['description'])
    
    def clear_message(self) -> None:
        """Clear the room message."""
        self.query_one("#room-message").update("")