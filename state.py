from typing import List, Dict, Any
import os, json
import time
import node, player, event
import storage as st

class GameState:
    def __init__(self, data: dict[str, Any]):
        self.player = player.Player.from_name(data['player'])
        if 'current_node' not in data:
            data['current_node'] = self.player.location
        self.node_manager = node.GameNodeManager(data['node_log'], data['current_node'])
        self.event_manager = event.EventManager(data['event_log'])
        self.current_node = self.node_manager.current_node
        if 'current_event' in data:
            self.current_event = self.event_manager.get_event(data['current_event'])
        else:
            self.current_event = self.event_manager.get_current_event()

    def add_event(self, event):
        self.event_manager.log_event(event)
    
    def move_to_node(self) -> None:
        """Move player to a new location node"""
        self.current_node = self.event_manager.get_event(self.current_event).end_node
        self.current_event = None
        self.player.location = self.current_node
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to dictionary for saving"""
        c_e = self.current_event.name if self.current_event else None

        return {
            "player": self.player.name,
            "event_log": self.event_manager.save(),
            "node_log": self.node_manager.save(),
            "current_event": c_e,
            "current_node": self.current_node.name
        }
    
    def save_game(self):
       """Save game state to file"""
       st.save_game(self.player.name, self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """Create game state from dictionary data"""
        data['player'] = st.load_player(data['player'])
        return cls(data)

    def get_event_consequence(self, event_name, event_stage):
        self.event_manager.get_consequence(event_name, event_stage)
        
if __name__ == '__main__':
    game_dict = {
        "player": "Tourist",
        "event_log": [],
        "node_log": [],
    }
    gs = GameState(game_dict)
    gs.save_game()