
import json
from typing import List, Any
import storage as st
import new_event as event    
    
class GameNode:

    def __init__(self, info: dict[str, Any]):
        self.name = info['name']
        self.characters = info['characters']
        self.description = info['description']
        self.events = info['events']
        self.connections = info['connections']
        self.items = info['items']
        if 'current_event' in info:
            self.current_event = info['current_event']
        elif len(self.events) > 0:
            self.current_event = event.Event.from_name(self.events[0])
        else:
            self.current_event = None
    
    @classmethod
    def from_name(cls, node_name) -> 'GameNode':
        info = st.get_node(node_name)
        return cls(info)

    def to_dict(self):
        return {
            "name": self.name,
            "characters": self.characters,
            "description": self.description,
            "events": self.events,
            "connections": self.connections,
            "items": self.items
        }
   
    def save(self):
        st.save_node(self.name, self.to_dict())
        return self.name

    def describe(self) -> str:
        """Return a description of this location."""
        chars = ", ".join(self.characters) or "no one"
        items = ", ".join(self.items) or "nothing"
        conns = ", ".join(self.connections) or "nowhere"
        return (
            f"Location: {self.name}\n"
            f"{self.description}\n"
            f"You see: {chars}.\n"
            f"Items here: {items}.\n"
            f"Paths lead to: {conns}."
        )
    
    
