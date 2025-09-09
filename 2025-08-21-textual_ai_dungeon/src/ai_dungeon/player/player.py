"""
Player management system.

This module contains the Player class that manages player state,
statistics, and interactions with the game world.
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from ai_dungeon.player.inventory import Inventory


@dataclass
class PlayerStats:
    """Player statistics and attributes."""
    strength: int = 10
    dexterity: int = 10
    intelligence: int = 10
    charisma: int = 10
    luck: int = 10
    
    @property
    def total_stats(self) -> int:
        """Get the sum of all stats."""
        return self.strength + self.dexterity + self.intelligence + self.charisma + self.luck
    
    def get_modifier(self, stat_name: str) -> int:
        """Get the modifier for a stat (similar to D&D system)."""
        stat_value = getattr(self, stat_name, 10)
        return (stat_value - 10) // 2
    
    def to_dict(self) -> Dict[str, int]:
        """Convert stats to dictionary."""
        return {
            "strength": self.strength,
            "dexterity": self.dexterity,
            "intelligence": self.intelligence,
            "charisma": self.charisma,
            "luck": self.luck
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "PlayerStats":
        """Create stats from dictionary."""
        return cls(
            strength=data.get("strength", 10),
            dexterity=data.get("dexterity", 10),
            intelligence=data.get("intelligence", 10),
            charisma=data.get("charisma", 10),
            luck=data.get("luck", 10)
        )


@dataclass
class Player:
    """Represents the player character."""
    
    name: str = "Adventurer"
    level: int = 1
    experience: int = 0
    inventory: Inventory = field(default_factory=Inventory)
    stats: PlayerStats = field(default_factory=PlayerStats)
    equipped_items: Dict[str, str] = field(default_factory=dict)  # slot -> item_name
    status_effects: Dict[str, int] = field(default_factory=dict)  # effect -> turns_remaining
    
    @property
    def experience_to_next_level(self) -> int:
        """Calculate experience needed for next level."""
        return (self.level * 100) - self.experience
    
    @property
    def carrying_capacity(self) -> int:
        """Calculate carrying capacity based on strength."""
        base_capacity = 50
        strength_bonus = self.stats.get_modifier("strength") * 5
        return base_capacity + strength_bonus
    
    def can_level_up(self) -> bool:
        """Check if player has enough experience to level up."""
        return self.experience >= (self.level * 100)
    
    def level_up(self) -> str:
        """Level up the player and return a description."""
        if not self.can_level_up():
            return "You don't have enough experience to level up."
        
        self.level += 1
        self.experience -= ((self.level - 1) * 100)
        
        # Increase stats slightly on level up
        import random
        stat_names = ["strength", "dexterity", "intelligence", "charisma", "luck"]
        chosen_stat = random.choice(stat_names)
        current_value = getattr(self.stats, chosen_stat)
        setattr(self.stats, chosen_stat, current_value + 1)
        
        # Update inventory capacity based on new strength
        self.inventory.max_weight = self.carrying_capacity
        
        return f"Level up! You are now level {self.level}. Your {chosen_stat} has increased!"
    
    def gain_experience(self, amount: int) -> str:
        """Gain experience points."""
        self.experience += amount
        result = f"You gained {amount} experience points."
        
        # Check for level up
        if self.can_level_up():
            result += " " + self.level_up()
        
        return result
    
    def equip_item(self, item_name: str, slot: str) -> str:
        """Equip an item from inventory."""
        item = self.inventory.get_item(item_name)
        if not item:
            return f"You don't have a {item_name} in your inventory."
        
        # Check if item can be equipped
        if item.item_type.value not in ["weapon", "armor"]:
            return f"You cannot equip the {item.name}."
        
        # Unequip current item if any
        if slot in self.equipped_items:
            old_item = self.equipped_items[slot]
            result = f"You unequip the {old_item} and equip the {item.name}."
        else:
            result = f"You equip the {item.name}."
        
        self.equipped_items[slot] = item.name
        return result
    
    def unequip_item(self, slot: str) -> str:
        """Unequip an item from a slot."""
        if slot not in self.equipped_items:
            return f"You don't have anything equipped in the {slot} slot."
        
        item_name = self.equipped_items.pop(slot)
        return f"You unequip the {item_name}."
    
    def add_status_effect(self, effect: str, duration: int) -> str:
        """Add a status effect to the player."""
        self.status_effects[effect] = duration
        return f"You are now affected by {effect} for {duration} turns."
    
    def remove_status_effect(self, effect: str) -> str:
        """Remove a status effect from the player."""
        if effect in self.status_effects:
            del self.status_effects[effect]
            return f"The {effect} effect has worn off."
        return f"You are not affected by {effect}."
    
    def process_turn(self) -> str:
        """Process effects that happen each turn."""
        messages = []
        
        # Decrease status effect durations
        effects_to_remove = []
        for effect, duration in self.status_effects.items():
            new_duration = duration - 1
            if new_duration <= 0:
                effects_to_remove.append(effect)
                messages.append(f"The {effect} effect has worn off.")
            else:
                self.status_effects[effect] = new_duration
        
        # Remove expired effects
        for effect in effects_to_remove:
            del self.status_effects[effect]
        
        return "\n".join(messages) if messages else ""
    
    def get_character_sheet(self) -> str:
        """Get a formatted character sheet display."""
        lines = [
            f"Character: {self.name}",
            f"Level: {self.level} (XP: {self.experience}/{self.level * 100})",
            "-" * 40,
            "Stats:",
            f"  Strength: {self.stats.strength} ({self.stats.get_modifier('strength'):+d})",
            f"  Dexterity: {self.stats.dexterity} ({self.stats.get_modifier('dexterity'):+d})",
            f"  Intelligence: {self.stats.intelligence} ({self.stats.get_modifier('intelligence'):+d})",
            f"  Charisma: {self.stats.charisma} ({self.stats.get_modifier('charisma'):+d})",
            f"  Luck: {self.stats.luck} ({self.stats.get_modifier('luck'):+d})",
            "-" * 40,
        ]
        
        if self.equipped_items:
            lines.append("Equipped Items:")
            for slot, item_name in self.equipped_items.items():
                lines.append(f"  {slot.title()}: {item_name}")
            lines.append("-" * 40)
        
        if self.status_effects:
            lines.append("Status Effects:")
            for effect, duration in self.status_effects.items():
                lines.append(f"  {effect} ({duration} turns remaining)")
            lines.append("-" * 40)
        
        lines.append(f"Carrying Capacity: {self.inventory.current_weight}/{self.carrying_capacity} kg")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary representation."""
        return {
            "name": self.name,
            "level": self.level,
            "experience": self.experience,
            "inventory": self.inventory.to_dict(),
            "stats": self.stats.to_dict(),
            "equipped_items": self.equipped_items,
            "status_effects": self.status_effects
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        """Create player from dictionary representation."""
        player = cls(
            name=data.get("name", "Adventurer"),
            level=data.get("level", 1),
            experience=data.get("experience", 0),
            equipped_items=data.get("equipped_items", {}),
            status_effects=data.get("status_effects", {})
        )
        
        # Load inventory
        if "inventory" in data:
            player.inventory = Inventory.from_dict(data["inventory"])
        
        # Load stats
        if "stats" in data:
            player.stats = PlayerStats.from_dict(data["stats"])
        
        # Update inventory capacity based on stats
        player.inventory.max_weight = player.carrying_capacity
        
        return player
