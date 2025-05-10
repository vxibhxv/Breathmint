"""
This module handles player-specific data and functionality.
"""
from typing import List, Dict, Any, Optional


class Player:
    """
    Class representing a player in the game
    """
    def __init__(self, info: dict):
        """Initialize a new player"""
        self.name = info.name
        self.health = info.health
        self.max_health = info.max_health
        self.inventory = info.inventory
        self.stats = info.stats
        self.location = info.location
        self.relationships = info.relationships
    
    def add_to_inventory(self, item: str) -> None:
        """Add an item to player inventory"""
        self.inventory.append(item)
    
    def remove_from_inventory(self, item: str) -> bool:
        """Remove an item from inventory if present"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def has_item(self, item: str) -> bool:
        """Check if player has a specific item"""
        return item in self.inventory
    
    def modify_health(self, amount: int) -> int:
        """Modify player health and return new value"""
        self.health += amount
        # Ensure health stays within bounds
        self.health = max(0, min(self.health, self.max_health))
        return self.health

    def is_alive(self) -> bool:
        """Check if player is alive"""
        return self.health > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player data to dictionary for saving"""
        return {
            "name": self.name,
            "health": self.health,
            "max_health": self.max_health,
            "inventory": self.inventory.copy(),
            "stats": self.stats.copy()
        }
    

def load_player(data: Dict[str, Any], player_name: str) -> 'Player':
    """Create a player instance from dictionary data"""
    input_entry = data.get(player_name)
    player = Player(input_entry)
    return player