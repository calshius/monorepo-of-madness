"""
World management system.

This module handles the game world, including locations, NPCs,
and world state management.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json
import os


# For now, I'll use relative imports that work when the package is properly installed
from ai_dungeon.core.models import Location, NPC, Item, ItemType


@dataclass
class World:
    """Manages the game world state."""
    
    locations: Dict[str, Location] = field(default_factory=dict)
    npcs: Dict[str, NPC] = field(default_factory=dict)
    items: Dict[str, Item] = field(default_factory=dict)
    global_flags: Dict[str, bool] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize the world with starting content."""
        if not self.locations:
            self._create_starting_world()
    
    def _create_starting_world(self):
        """Create the initial game world with some basic locations and items."""
        # Create starting items
        rusty_key = Item(
            name="rusty key",
            description="An old, rusty key. It looks like it might open something important.",
            item_type=ItemType.KEY,
            weight=0,
            value=5
        )
        
        ancient_book = Item(
            name="ancient tome",
            description="A leather-bound book filled with mysterious symbols and arcane knowledge.",
            item_type=ItemType.MISC,
            weight=2,
            value=50,
            properties={"readable": True, "magic": True}
        )
        
        glowing_crystal = Item(
            name="glowing crystal",
            description="A beautiful crystal that emits a soft, warm light.",
            item_type=ItemType.TREASURE,
            weight=1,
            value=100,
            properties={"light_source": True}
        )
        
        # Store items in world registry
        self.items["rusty_key"] = rusty_key
        self.items["ancient_tome"] = ancient_book
        self.items["glowing_crystal"] = glowing_crystal
        
        # Create starting locations
        starting_room = Location(
            name="starting_room",
            description="You find yourself in a dimly lit stone chamber. Ancient runes cover the walls, "
                       "and a mysterious energy fills the air. This appears to be some kind of ritual chamber.",
            exits={"north": "corridor", "east": "library"},
            items=["rusty_key"],
            first_visit_description="You awaken in this strange place, your memories hazy. The stone beneath "
                                  "your feet is cold, and the air crackles with magical energy. How did you get here?"
        )
        
        corridor = Location(
            name="corridor",
            description="A long, narrow corridor stretches before you. Torches mounted on the walls cast "
                       "dancing shadows. The passage continues deeper into the structure.",
            exits={"south": "starting_room", "north": "great_hall", "west": "storage_room"},
            items=[]
        )
        
        library = Location(
            name="library",
            description="You enter a vast library with towering bookshelves that disappear into the shadows above. "
                       "Dust motes dance in shafts of light filtering through stained glass windows.",
            exits={"west": "starting_room", "up": "tower_study"},
            items=["ancient_tome"],
            npcs=["librarian"]
        )
        
        great_hall = Location(
            name="great_hall",
            description="An enormous hall with vaulted ceilings and massive stone pillars. Banners hang "
                       "from the rafters, though their symbols are faded with age.",
            exits={"south": "corridor", "east": "throne_room", "west": "kitchen"},
            items=[]
        )
        
        storage_room = Location(
            name="storage_room",
            description="A cluttered storage room filled with crates, barrels, and forgotten treasures. "
                       "Cobwebs hang in every corner.",
            exits={"east": "corridor"},
            items=["glowing_crystal"]
        )
        
        # Store locations in world registry
        self.locations["starting_room"] = starting_room
        self.locations["corridor"] = corridor
        self.locations["library"] = library
        self.locations["great_hall"] = great_hall
        self.locations["storage_room"] = storage_room
        
        # Create starting NPCs
        librarian = NPC(
            name="Ancient Librarian",
            description="A mysterious figure in flowing robes, their face hidden in shadow. They seem to know "
                       "far more than they let on.",
            dialogue_state="initial",
            disposition="friendly",
            properties={"knows_about": ["ancient_tome", "tower_study", "history"]}
        )
        
        # Add some hostile creatures for combat
        shadow_beast = NPC(
            name="Shadow Beast",
            description="A dark, writhing creature with glowing red eyes. It seems drawn to magical energy "
                       "and appears hostile.",
            dialogue_state="hostile",
            disposition="hostile",
            properties={"creature_type": "shadow", "level": 1}
        )
        
        stone_guardian = NPC(
            name="Stone Guardian",
            description="An ancient stone statue that has come to life. Its eyes glow with mystical power "
                       "as it protects this sacred place.",
            dialogue_state="guardian",
            disposition="hostile",
            properties={"creature_type": "construct", "level": 2}
        )
        
        self.npcs["librarian"] = librarian
        self.npcs["shadow_beast"] = shadow_beast
        self.npcs["stone_guardian"] = stone_guardian
        
        # Add some creatures to locations
        great_hall.npcs.append("shadow_beast")  # Add enemy to great hall
        storage_room.npcs.append("stone_guardian")  # Add guardian to storage
    
    def get_location(self, location_name: str) -> Optional[Location]:
        """Get a location by name."""
        return self.locations.get(location_name)
    
    def add_location(self, location: Location) -> None:
        """Add a new location to the world."""
        self.locations[location.name] = location
    
    def get_npc(self, npc_name: str) -> Optional[NPC]:
        """Get an NPC by name."""
        # Try exact match first
        if npc_name in self.npcs:
            return self.npcs[npc_name]
        
        # Try partial match
        for key, npc in self.npcs.items():
            if npc_name.lower() in npc.name.lower() or npc.name.lower() in npc_name.lower():
                return npc
        
        return None
    
    def add_npc(self, npc: NPC, location_name: str) -> None:
        """Add an NPC to the world and place them in a location."""
        npc_key = npc.name.lower().replace(" ", "_")
        self.npcs[npc_key] = npc
        
        if location_name in self.locations:
            location = self.locations[location_name]
            if npc_key not in location.npcs:
                location.npcs.append(npc_key)
    
    def get_item(self, item_name: str) -> Optional[Item]:
        """Get an item template by name."""
        # Try exact match first
        if item_name in self.items:
            return self.items[item_name]
        
        # Try partial match
        for key, item in self.items.items():
            if item_name.lower() in item.name.lower() or item.name.lower() in item_name.lower():
                return item
        
        return None
    
    def add_item_to_location(self, item_name: str, location_name: str) -> bool:
        """Add an item to a location."""
        if location_name not in self.locations:
            return False
        
        if item_name not in self.items:
            return False
        
        location = self.locations[location_name]
        if item_name not in location.items:
            location.items.append(item_name)
            return True
        
        return False
    
    def remove_item_from_location(self, item_name: str, location_name: str) -> bool:
        """Remove an item from a location."""
        if location_name not in self.locations:
            return False
        
        location = self.locations[location_name]
        if item_name in location.items:
            location.items.remove(item_name)
            return True
        
        return False
    
    def set_global_flag(self, flag_name: str, value: bool) -> None:
        """Set a global world flag."""
        self.global_flags[flag_name] = value
    
    def get_global_flag(self, flag_name: str) -> bool:
        """Get a global world flag."""
        return self.global_flags.get(flag_name, False)
    
    def get_npcs_in_location(self, location_name: str) -> List[NPC]:
        """Get all NPCs in a specific location."""
        location = self.get_location(location_name)
        if not location:
            return []
        
        npcs = []
        for npc_key in location.npcs:
            npc = self.npcs.get(npc_key)
            if npc:
                npcs.append(npc)
        
        return npcs
    
    def get_items_in_location(self, location_name: str) -> List[Item]:
        """Get all items in a specific location."""
        location = self.get_location(location_name)
        if not location:
            return []
        
        items = []
        for item_key in location.items:
            item = self.items.get(item_key)
            if item:
                items.append(item)
        
        return items
    
    def get_location_description(self, location_name: str, first_visit: bool = False) -> str:
        """Get a formatted description of a location."""
        location = self.get_location(location_name)
        if not location:
            return "You are nowhere."
        
        # Start with main description
        if first_visit and location.first_visit_description:
            description = location.first_visit_description + "\n\n" + location.description
        else:
            description = location.description
        
        # Add NPCs
        npcs = self.get_npcs_in_location(location_name)
        if npcs:
            npc_names = [npc.name for npc in npcs]
            description += f"\n\nYou see: {', '.join(npc_names)}"
        
        # Add items
        items = self.get_items_in_location(location_name)
        if items:
            item_names = [item.name for item in items]
            description += f"\n\nYou notice: {', '.join(item_names)}"
        
        # Add exits
        if location.exits:
            exits = list(location.exits.keys())
            description += f"\n\nExits: {', '.join(exits)}"
        
        return description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert world to dictionary representation."""
        return {
            "locations": {name: loc.to_dict() for name, loc in self.locations.items()},
            "npcs": {name: npc.to_dict() for name, npc in self.npcs.items()},
            "items": {name: item.to_dict() for name, item in self.items.items()},
            "global_flags": self.global_flags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "World":
        """Create world from dictionary representation."""
        world = cls()
        
        # Clear default world first
        world.locations.clear()
        world.npcs.clear()
        world.items.clear()
        
        # Load locations
        for name, loc_data in data.get("locations", {}).items():
            world.locations[name] = Location.from_dict(loc_data)
        
        # Load NPCs
        for name, npc_data in data.get("npcs", {}).items():
            world.npcs[name] = NPC(**npc_data)
        
        # Load items
        for name, item_data in data.get("items", {}).items():
            world.items[name] = Item.from_dict(item_data)
        
        # Load global flags
        world.global_flags = data.get("global_flags", {})
        
        return world
    
    def save_to_file(self, filepath: str) -> None:
        """Save world to a JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> "World":
        """Load world from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
