"""
Event class for text adventure game.
This module handles game events and event tracking.
"""
from typing import List, Dict, Any
import storage as st

class Event:
    """
    Class representing a single game event
    """
    def __init__(self, data: dict[str, Any]):
        """Initialize a new event"""
        self.name=data["name"]
        self.description=data["description"]
        self.event_type=data["event_type"]
        self.characters = data["characters"]
        self.start_node=data["start_node"]
        self.end_node=data["end_node"]
        self.consequence=data["consequence"]
    
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "event_type": self.event_type,
            "event_stages": self.event_stages,
            "characters": self.characters,
            "start_node": self.start_node,
            "end_node": self.end_node,
            "consequence": self.consequence
        }
    
    @classmethod
    def from_name(cls, event_name) -> 'Event':
        data = st.get_event(event_name)
        return cls(data)

    def save(self):
        if self.event_name:
            st.save_event(self.event_name, self.to_dict())
    
    def describe(self) -> str:
        chars = ", ".join(self.characters) or "no one"
        return (
            f"Event '{self.name}' ({self.event_type}):\n"
            f"{self.description}\n"
            f"Involves: {chars}.\n"
            f"Leads from {self.start_node} to {self.end_node}.\n"
        )

    def handle_event(self) -> Any:
        """
        Resolve the event based on its type.
        Returns something meaningful to GameState.
        """
        if self.event_type == "conversation":
            item = "mysterious_key"  # Example reward
            return {
                "type": "conversation",
                "story": self.consequence,
                "item_reward": item
            }

        elif self.event_type == "movement":
            return {
                "type": "movement",
                "actions": [{"move_to": self.end_node}]
            }

        return {"type": "unknown"}