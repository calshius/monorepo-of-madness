from .base_room import BaseRoom
import random


class WizardRoom(BaseRoom):
    """A room containing a wise wizard."""
    
    def __init__(self):
        super().__init__()
        self.wizards = [
            "Ancient Sage",
            "Mystical Oracle", 
            "Wise Enchanter",
            "Scholarly Mage",
            "Hermit Wizard"
        ]
        self.wizard = random.choice(self.wizards)
        self.advice = [
            "The path to victory lies in courage, not strength",
            "Beware the shadows that follow your steps",
            "Your destiny awaits beyond the eastern walls", 
            "Trust in your instincts, young adventurer",
            "The greatest treasure is knowledge itself"
        ]
        self.wisdom = random.choice(self.advice)
    
    def get_name(self) -> str:
        return "Wizard's Chamber"
    
    def get_description(self) -> str:
        return f"A {self.wizard} sits surrounded by ancient books and glowing crystals. The air hums with magic."
    
    def get_emoji(self) -> str:
        return "🧙‍♂️"
    
    def enter(self) -> str:
        self.visited = True
        return f"The {self.wizard} looks up and says: '{self.wisdom}'"