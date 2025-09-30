from .base_room import BaseRoom
import random


class MerchantRoom(BaseRoom):
    """A room containing a friendly merchant."""
    
    def __init__(self):
        super().__init__()
        self.merchants = [
            "Old Wizard Vendor",
            "Traveling Trader", 
            "Mysterious Shopkeeper",
            "Friendly Halfling",
            "Exotic Goods Seller"
        ]
        self.merchant = random.choice(self.merchants)
        self.items = [
            "Health Potion",
            "Magic Sword",
            "Shield of Protection",
            "Ancient Map",
            "Lucky Charm"
        ]
        self.item = random.choice(self.items)
    
    def get_name(self) -> str:
        return "Merchant's Shop"
    
    def get_description(self) -> str:
        return f"A {self.merchant} greets you warmly. They have a {self.item} for sale."
    
    def get_emoji(self) -> str:
        return "🏪"
    
    def enter(self) -> str:
        self.visited = True
        return f"Welcome, traveler! The {self.merchant} offers you a {self.item}!"