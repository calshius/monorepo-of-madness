"""
Player inventory management system.

This module handles all inventory-related operations including
item management, weight calculations, and inventory interactions.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from ai_dungeon.core.models import Item, ItemType


@dataclass
class Inventory:
    """Manages the player's inventory with weight and capacity constraints."""
    
    items: Dict[str, Item] = field(default_factory=dict)
    max_weight: int = 50
    max_items: int = 20
    
    @property
    def current_weight(self) -> int:
        """Calculate the total weight of all items in inventory."""
        return sum(item.weight for item in self.items.values())
    
    @property
    def item_count(self) -> int:
        """Get the number of items in inventory."""
        return len(self.items)
    
    @property
    def is_full(self) -> bool:
        """Check if inventory is at maximum item capacity."""
        return self.item_count >= self.max_items
    
    @property
    def is_overweight(self) -> bool:
        """Check if inventory exceeds weight limit."""
        return self.current_weight > self.max_weight
    
    def can_add_item(self, item: Item) -> bool:
        """Check if an item can be added to the inventory."""
        if self.is_full:
            return False
        if self.current_weight + item.weight > self.max_weight:
            return False
        return True
    
    def add_item(self, item: Item) -> bool:
        """Add an item to the inventory if possible."""
        if not self.can_add_item(item):
            return False
        
        # If item already exists, we could stack them or just add another
        # For now, we'll just add with a unique key
        base_name = item.name
        counter = 1
        item_key = base_name
        
        while item_key in self.items:
            item_key = f"{base_name}_{counter}"
            counter += 1
        
        self.items[item_key] = item
        return True
    
    def remove_item(self, item_name: str) -> Optional[Item]:
        """Remove and return an item from the inventory."""
        # Try exact match first
        if item_name in self.items:
            return self.items.pop(item_name)
        
        # Try to find by partial match
        for key, item in self.items.items():
            if item_name.lower() in item.name.lower() or item.name.lower() in item_name.lower():
                return self.items.pop(key)
        
        return None
    
    def get_item(self, item_name: str) -> Optional[Item]:
        """Get an item from inventory without removing it."""
        # Try exact match first
        if item_name in self.items:
            return self.items[item_name]
        
        # Try to find by partial match
        for key, item in self.items.items():
            if item_name.lower() in item.name.lower() or item.name.lower() in item_name.lower():
                return item
        
        return None
    
    def has_item(self, item_name: str) -> bool:
        """Check if inventory contains an item."""
        return self.get_item(item_name) is not None
    
    def list_items(self) -> List[Item]:
        """Get a list of all items in inventory."""
        return list(self.items.values())
    
    def list_items_by_type(self, item_type: ItemType) -> List[Item]:
        """Get a list of items of a specific type."""
        return [item for item in self.items.values() if item.item_type == item_type]
    
    def get_total_value(self) -> int:
        """Calculate the total value of all items in inventory."""
        return sum(item.value for item in self.items.values())
    
    def use_item(self, item_name: str) -> Optional[str]:
        """Use an item from inventory and return the result."""
        item = self.get_item(item_name)
        if not item:
            return None
        
        if not item.usable:
            return f"You cannot use the {item.name}."
        
        # If item is consumable, remove it from inventory
        if item.consumable:
            self.remove_item(item_name)
            return f"You used the {item.name}. It has been consumed."
        else:
            return f"You used the {item.name}."
    
    def get_inventory_display(self) -> str:
        """Get a formatted string display of the inventory."""
        if not self.items:
            return "Your inventory is empty."
        
        lines = ["Your inventory:"]
        lines.append(f"Weight: {self.current_weight}/{self.max_weight} kg")
        lines.append(f"Items: {self.item_count}/{self.max_items}")
        lines.append("-" * 40)
        
        # Group items by type
        by_type = {}
        for item in self.items.values():
            if item.item_type not in by_type:
                by_type[item.item_type] = []
            by_type[item.item_type].append(item)
        
        for item_type, items in by_type.items():
            lines.append(f"{item_type.value.title()}:")
            for item in items:
                weight_str = f"({item.weight}kg)" if item.weight > 0 else ""
                value_str = f"[{item.value}g]" if item.value > 0 else ""
                lines.append(f"  - {item.name} {weight_str} {value_str}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Convert inventory to dictionary representation."""
        return {
            "items": {key: item.to_dict() for key, item in self.items.items()},
            "max_weight": self.max_weight,
            "max_items": self.max_items
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Inventory":
        """Create inventory from dictionary representation."""
        inventory = cls(
            max_weight=data.get("max_weight", 50),
            max_items=data.get("max_items", 20)
        )
        
        items_data = data.get("items", {})
        for key, item_data in items_data.items():
            inventory.items[key] = Item.from_dict(item_data)
        
        return inventory
