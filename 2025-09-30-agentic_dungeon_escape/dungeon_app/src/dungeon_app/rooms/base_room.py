from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseRoom(ABC):
    """Base class for all room types in the dungeon."""
    
    def __init__(self):
        self.visited = False
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the room."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return the description of what the player sees."""
        pass
    
    @abstractmethod
    def get_emoji(self) -> str:
        """Return an emoji representing the room."""
        pass
    
    def enter(self) -> str:
        """Called when the player enters the room. Returns a message."""
        self.visited = True
        return f"You enter the {self.get_name()}"
    
    def get_display_info(self) -> Dict[str, Any]:
        """Return all display information for the room."""
        return {
            "name": self.get_name(),
            "description": self.get_description(),
            "emoji": self.get_emoji(),
            "visited": self.visited
        }