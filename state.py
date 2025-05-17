from typing import List, Dict, Any
import node as node
import player as player
import event as event
import storage as st
import json

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
            "current_node": self.current_node.save(),
            "current_event": self.current_event.save()
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
        IMAGE_DIR = "images/"
        if self.current_event:
            image_path = IMAGE_DIR + self.current_node.name + '-' + self.current_event.name + '.jpg'
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
            self.conversation_turns += 1

            if self.conversation_turns == 1:
                self.conversation_history = []
                self.locked_event = "conversation"

                if isinstance(self.current_event.consequence, list):
                    return "\n".join(self.current_event.consequence[:2])
                else:
                    return self.current_event.consequence  # fallback for string-type

            elif self.conversation_turns in {2, 3}:
                return {
                    "status": "awaiting_player_question",
                    "context": self.current_event.consequence,
                    "history": self.conversation_history
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
