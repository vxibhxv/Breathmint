"""
Node class for text adventure game.
This module handles game nodes (locations) and their properties.
"""
from typing import List, Dict, Any, Optional, Union
import json


class Connection:
    """
    Class representing a connection between nodes
    """
    def __init__(self, target_id: str, required_item: Optional[str] = None, 
                 required_flag: Optional[str] = None, description: Optional[str] = None):
        """Initialize a connection between nodes"""
        self.target_id = target_id
        self.required_item = required_item
        self.required_flag = required_flag
        self.description = description or f"Path to {target_id}"
    
    def is_available(self, player, game_state) -> bool:
        """Check if this connection is available based on requirements"""
        if self.required_item and not player.has_item(self.required_item):
            return False
        if self.required_flag and not game_state.has_flag(self.required_flag):
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert connection to dictionary for saving"""
        result = {"target_id": self.target_id}
        if self.required_item:
            result["required_item"] = self.required_item
        if self.required_flag:
            result["required_flag"] = self.required_flag
        if self.description:
            result["description"] = self.description
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Connection':
        """Create a connection from dictionary data"""
        return cls(
            target_id=data["target_id"],
            required_item=data.get("required_item"),
            required_flag=data.get("required_flag"),
            description=data.get("description")
        )


class Choice:
    """
    Class representing a special choice available in a node
    """
    def __init__(self, text: str, consequences: Dict[str, Any] = None):
        """Initialize a choice"""
        self.text = text
        self.consequences = consequences or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert choice to dictionary for saving"""
        return {
            "text": self.text,
            "consequences": self.consequences.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Choice':
        """Create a choice from dictionary data"""
        return cls(
            text=data["text"],
            consequences=data.get("consequences", {})
        )


class Node:
    """
    Class representing a location in the game
    """
    def __init__(self, node_id: str, name: str, description: str):
        """Initialize a node"""
        self.id = node_id
        self.name = name
        self.description = description
        self.connections: List[Connection] = []
        self.choices: List[Choice] = []
        self.items: List[str] = []
        self.first_visit_text: Optional[str] = None
        self.revisit_text: Optional[str] = None
        self.visited = False
    
    def add_connection(self, connection: Connection) -> None:
        """Add a connection to another node"""
        self.connections.append(connection)
    
    def add_simple_connection(self, target_id: str) -> None:
        """Add a simple connection without requirements"""
        self.connections.append(Connection(target_id))
    
    def add_choice(self, choice: Choice) -> None:
        """Add a special choice to this node"""
        self.choices.append(choice)
    
    def add_item(self, item: str) -> None:
        """Add an item that can be found in this node"""
        if item not in self.items:
            self.items.append(item)
    
    def remove_item(self, item: str) -> bool:
        """Remove an item from this node"""
        if item in self.items:
            self.items.remove(item)
            return True
        return False
    
    def get_available_connections(self, player, game_state) -> List[Connection]:
        """Get connections that are currently available"""
        return [conn for conn in self.connections if conn.is_available(player, game_state)]
    
    def get_description(self) -> str:
        """Get the appropriate description based on visit status"""
        if not self.visited and self.first_visit_text:
            return self.first_visit_text
        elif self.visited and self.revisit_text:
            return self.revisit_text
        return self.description
    
    def mark_visited(self) -> None:
        """Mark node as visited"""
        self.visited = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary for saving"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "connections": [conn.to_dict() for conn in self.connections],
            "choices": [choice.to_dict() for choice in self.choices],
            "items": self.items.copy(),
            "first_visit_text": self.first_visit_text,
            "revisit_text": self.revisit_text,
            "visited": self.visited
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Node':
        """Create a node from dictionary data"""
        node = cls(
            node_id=data["id"],
            name=data["name"],
            description=data["description"]
        )
        
        # Add connections
        for conn_data in data.get("connections", []):
            if isinstance(conn_data, str):
                # Handle simple string connections
                node.add_simple_connection(conn_data)
            else:
                # Handle full connection objects
                node.add_connection(Connection.from_dict(conn_data))
        
        # Add choices
        for choice_data in data.get("choices", []):
            node.add_choice(Choice.from_dict(choice_data))
        
        # Add other properties
        node.items = data.get("items", []).copy()
        node.first_visit_text = data.get("first_visit_text")
        node.revisit_text = data.get("revisit_text")
        node.visited = data.get("visited", False)
        
        return node
    
    @classmethod
    def load_from_file(cls, filepath: str) -> Optional['Node']:
        """Load a node from a JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return cls.from_dict(data)
        except Exception as e:
            print(f"Error loading node from {filepath}: {e}")
            return None
    
    def save_to_file(self, filepath: str) -> bool:
        """Save node to a JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving node to {filepath}: {e}")
            return False