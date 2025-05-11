import json
from typing import List

class Connection:
    def __init__(self, node_a, node_b, con_event):
        self.node_a = node_a
        self.node_b = node_b
        self.con_event = con_event
    
    
class GameNode:

    def __init__(self, characters, events, connections, items):
        self.characters: List[str] = characters
        self.events: List[str] = events
        self.connections: None
        self.items: List[str] = items
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            characters = data['characters'],
            events= data['events'],
            connections = data['connections'],
            items = data['items']
        )

    def to_dict(self):
        return {
            "characters": self.characters,
            "events": self.events,
            "connections": self.connections,
            "items": self.items
        }
