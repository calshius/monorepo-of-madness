"""
Core data models for the AI Dungeon game.

This module contains the fundamental data structures used throughout
the game, including game state, locations, items, and NPCs.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json


class CommandType(Enum):
    """Types of commands that can be processed by the game engine."""
    MOVEMENT = "movement"
    INVENTORY = "inventory"
    INTERACTION = "interaction"
    SYSTEM = "system"
    DIALOGUE = "dialogue"
    UNKNOWN = "unknown"


class ItemType(Enum):
    """Types of items that can exist in the game world."""
    WEAPON = "weapon"
    ARMOR = "armor"
    KEY = "key"
    CONSUMABLE = "consumable"
    TREASURE = "treasure"
    MISC = "misc"


@dataclass
class Item:
    """Represents an item in the game world."""
    name: str
    description: str
    item_type: ItemType = ItemType.MISC
    weight: int = 1
    value: int = 0
    properties: Dict[str, Any] = field(default_factory=dict)
    usable: bool = False
    consumable: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type.value,
            "weight": self.weight,
            "value": self.value,
            "properties": self.properties,
            "usable": self.usable,
            "consumable": self.consumable
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        """Create item from dictionary representation."""
        return cls(
            name=data["name"],
            description=data["description"],
            item_type=ItemType(data.get("item_type", "misc")),
            weight=data.get("weight", 1),
            value=data.get("value", 0),
            properties=data.get("properties", {}),
            usable=data.get("usable", False),
            consumable=data.get("consumable", False)
        )


@dataclass
class NPC:
    """Represents a non-player character in the game."""
    name: str
    description: str
    dialogue_state: str = "initial"
    dialogue_history: List[str] = field(default_factory=list)
    disposition: str = "neutral"  # friendly, neutral, hostile
    inventory: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert NPC to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "dialogue_state": self.dialogue_state,
            "dialogue_history": self.dialogue_history,
            "disposition": self.disposition,
            "inventory": self.inventory,
            "properties": self.properties
        }


@dataclass
class Location:
    """Represents a location in the game world."""
    name: str
    description: str
    exits: Dict[str, str] = field(default_factory=dict)  # direction -> location_name
    items: List[str] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)
    first_visit_description: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    generated_by_ai: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert location to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "exits": self.exits,
            "items": self.items,
            "npcs": self.npcs,
            "first_visit_description": self.first_visit_description,
            "properties": self.properties,
            "generated_by_ai": self.generated_by_ai
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Location":
        """Create location from dictionary representation."""
        return cls(
            name=data["name"],
            description=data["description"],
            exits=data.get("exits", {}),
            items=data.get("items", []),
            npcs=data.get("npcs", []),
            first_visit_description=data.get("first_visit_description"),
            properties=data.get("properties", {}),
            generated_by_ai=data.get("generated_by_ai", False)
        )


@dataclass
class GameState:
    """Represents the current state of the game world."""
    current_location: str = "starting_room"
    health: int = 100
    max_health: int = 100
    score: int = 0
    turn_count: int = 0
    visited_locations: List[str] = field(default_factory=list)
    game_flags: Dict[str, bool] = field(default_factory=dict)
    active_quests: List[str] = field(default_factory=list)
    completed_quests: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to dictionary representation."""
        return {
            "current_location": self.current_location,
            "health": self.health,
            "max_health": self.max_health,
            "score": self.score,
            "turn_count": self.turn_count,
            "visited_locations": self.visited_locations,
            "game_flags": self.game_flags,
            "active_quests": self.active_quests,
            "completed_quests": self.completed_quests
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameState":
        """Create game state from dictionary representation."""
        return cls(
            current_location=data.get("current_location", "starting_room"),
            health=data.get("health", 100),
            max_health=data.get("max_health", 100),
            score=data.get("score", 0),
            turn_count=data.get("turn_count", 0),
            visited_locations=data.get("visited_locations", []),
            game_flags=data.get("game_flags", {}),
            active_quests=data.get("active_quests", []),
            completed_quests=data.get("completed_quests", [])
        )
    
    def save_to_file(self, filepath: str) -> None:
        """Save game state to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> "GameState":
        """Load game state from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


@dataclass
class GameCommand:
    """Represents a processed command from the player."""
    raw_command: str
    command_type: CommandType
    action: str
    target: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """String representation of the command."""
        return f"GameCommand({self.action}, target={self.target}, type={self.command_type.value})"
