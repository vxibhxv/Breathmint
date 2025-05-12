from typing import List, Dict, Any
import os, json
import time
import player

class GameState:
    def __init__(self, event_manager, player, current_node, current_event, character_manager):
        self.event_manager = event_manager
        self.player = player
        self.current_node = current_node
        self.current_event = current_event
        self.character_manager = character_manager
    
    def add_event(self, event):
        self.event_manager.log_event(event)
    
    def get_recent_events(self, count: int = 5) -> List[str]:
        """Get the most recent story events"""
        recent_events = self.event_manager.get_recent_events(count)
        return [str(event) for event in recent_events]
    
    def move_to_node(self) -> None:
        """Move player to a new location node"""
        self.current_node = self.event_manager.get_event(self.current_event).end_node
        self.current_event = None
        self.player.location = self.current_node
        
    
    def set_flag(self, flag_name: str, value: bool = True) -> None:
        """Set a game flag"""
        
    
    def has_flag(self, flag_name: str) -> bool:
        """Check if a flag is set and true"""
        
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to dictionary for saving"""
        return {
            "player": self.player.to_dict(),
            "event_log": self.event_manager.event_log,
            "current_event": self.current_event,
            "current_node": self.current_node,
            "current_event": self.current_event
        }
    
    def save_game(self, save_dir: str = "./data/saves") -> bool:
        """Save current game state to file"""
        save_file = os.path.join(save_dir, f"savegame_{time.time()}.json")
        with open(save_file, 'w+') as f:
            json.dump(self.to_dict(), f, indent=2)
        return True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """Create game state from dictionary data"""
        player = player.load_player(data['player'])
        current_node = data['current_node']
        current_event = data['current_event']
        
        return cls(
            player = data['Player'],

        )
        
    
    @classmethod
    def load_game(cls, save_file: str = "savegame.json"):
        """Load game state from file"""
        
    
    def to_context_dict(self) -> Dict[str, Any]:
        """Convert state to a dictionary suitable for AI context"""