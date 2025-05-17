from typing import List, Dict, Any
import node as node
import player as player
import event as event
import storage as st
import json
import subprocess

class GameState:
    def __init__(self, data: dict[str, Any]):
        self.player = player.Player.from_name(data['player'])
        
        # Set current node information
        if 'current_node' not in data:
            data['current_node'] = self.player.location
        self.current_node = node.GameNode.from_name(data['current_node'])

        # Set current event information
        self.current_event = self.current_node.current_event
        self.conversation_turns = 0
        self.locked_event = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to dictionary for saving"""
        op = {
            "player": self.player.save(),
        }
        return op
    
    def save_game(self):
       """Save game state to file"""
       st.save_game(self.player.name, self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """Create game state from dictionary data"""
        return cls(data)
    
    def respond(self, text_response: str) -> str:
        # Write to a file to upload to frontend
        if self.current_event:
            image_path = self.current_node.name + '-' + self.current_event.name
        else:
            image_path = None
        op = {
            "image_path": image_path,
            "text_response": text_response,
            "node_name": self.current_node.name,
            "node_connections": self.current_node.connections,
            "player_name": self.player.name,
            "player_health": self.player.health,
            "player_inventory": self.player.inventory,

        }
        file_path = 'frontend/public/response.json'
        with open(file_path, "w+") as f:
            json.dump(op, f, indent=2)
        return op
    
    def describe(self) -> str:
        """Combine player, node, and event descriptions into one narrative."""
        parts = [
            self.player.describe(),
            "",
            self.current_node.describe(),
            "",
            (self.current_event.describe() if self.current_event else "No event in progress.")
        ]
        return "\n".join(parts)

    def move_to(self, node_name: str) -> bool:
        """
        Attempts to move the player to the specified node.
        Returns True if successful, False otherwise.
        """
        if node_name in self.current_node.connections:
            self.conversation_turns = 0
            self.locked_event = None
            new_node = node.GameNode.from_name(node_name)
            self.current_node = new_node
            self.player.location = node_name
            self.current_event = self.current_node.current_event
            return True
        return False

    def perform_event(self) -> Any:
        if not self.current_event:
            return "There is no event to perform."

        if self.current_event.event_type == "conversation":
            self.locked_event = "conversation"
            if self.conversation_turns >= len(self.current_event.consequence):
                self.move_to(self.current_event.end_node)
                return {
                    "status": "movement_complete",
                    "location": self.current_node.name,
                    "description": self.current_node.describe()
                }
            else:
                response = self.current_event.consequence[self.conversation_turns]
                self.conversation_turns += 1
                return {
                    "status": "awaiting_player_question",
                    "response": response, 
                    "location": self.current_node.name
                }
        elif self.current_event.event_type == "combat":
            self.locked_event = "combat"
            subprocess.run(["python", "combat.py", self.current_event.name])
            self.move_to(self.current_event.end_node)
            return {
                "status": "movement_complete",
                "location": self.current_node.name,
                "description": self.current_node.describe()
            }
        else:
            self.move_to(self.current_event.end_node)
            self.conversation_turns = 0
            self.conversation_history = []
            self.locked_event = None
            return {
                "status": "movement_complete",
                "location": self.current_node.name,
                "description": self.current_node.describe()
            }
