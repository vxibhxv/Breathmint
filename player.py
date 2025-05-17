from typing import List, Dict, Any, Optional
import json
import storage as st

class Player:
    """
    Class representing a player in the game
    """
    def __init__(self, info: dict):
        """Initialize a new player"""
        # import pdb; pdb.set_trace()
        self.name = info['name']
        self.health = info['health']
        self.max_health = info['max_health']
        self.inventory = info['inventory']
        self.stats = info['stats']
        self.location = info['location']
        self.relationships = info['relationships']
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player data to dictionary for saving"""
        return {
            "name": self.name,
            "health": self.health,
            "max_health": self.max_health,
            "inventory": self.inventory.copy(),
            "stats": self.stats.copy(),
            "location": self.location,
            "relationships": self.relationships
        }
    
    @classmethod
    def from_name(cls, player_name)-> 'Player':
        data = st.get_player(player_name)
        return cls(data)
    
    def save(self):
        data = self.to_dict()
        st.save_player(self.name, data)
    
    def describe(self) -> str:
        """Return a summary of the player’s status."""
        inv = ", ".join(self.inventory) or "nothing"
        stats = ", ".join(f"{k}: {v}" for k, v in self.stats.items())
        return (
            f"You are {self.name}. "
            f"Health: {self.health}/{self.max_health}. "
            f"Inventory: {inv}. "
            f"Stats: {stats}. "
            f"Current location: {self.location}."
        )