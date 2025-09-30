from .base_room import BaseRoom
import random


class RoadRoom(BaseRoom):
    """A peaceful road or pathway room."""
    
    def __init__(self):
        super().__init__()
        self.road_types = [
            "Stone Bridge",
            "Forest Path", 
            "Mountain Trail",
            "Cobblestone Road",
            "Winding Pathway"
        ]
        self.road_type = random.choice(self.road_types)
        self.features = [
            "wildflowers blooming alongside",
            "ancient stone markers",
            "a gentle breeze rustling leaves", 
            "distant bird songs",
            "sunlight filtering through trees"
        ]
        self.feature = random.choice(self.features)
    
    def get_name(self) -> str:
        return "Peaceful Path"
    
    def get_description(self) -> str:
        return f"You walk along a {self.road_type} with {self.feature}. It's calm and peaceful here."
    
    def get_emoji(self) -> str:
        return "🛤️"
    
    def enter(self) -> str:
        self.visited = True
        return f"You find yourself on a {self.road_type}. The journey continues!"