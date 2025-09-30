from .base_room import BaseRoom
import random


class EnemyRoom(BaseRoom):
    """A room containing an enemy encounter."""
    
    def __init__(self):
        super().__init__()
        self.enemies = [
            "Goblin Warrior",
            "Skeleton Archer", 
            "Dark Wolf",
            "Shadow Assassin",
            "Orc Brute"
        ]
        self.enemy = random.choice(self.enemies)
    
    def get_name(self) -> str:
        return "Enemy Lair"
    
    def get_description(self) -> str:
        return f"A menacing {self.enemy} blocks your path! The air is thick with danger."
    
    def get_emoji(self) -> str:
        return "⚔️"
    
    def enter(self) -> str:
        self.visited = True
        return f"You encounter a {self.enemy} ready for battle!"