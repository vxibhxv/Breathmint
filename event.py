"""
Event class for text adventure game.
This module handles game events and event tracking.
"""
from typing import List, Dict, Any, Optional
import Path, json


class Event:
    """
    Class representing a single game event
    """
    def __init__(self, description: str, event_type: str, start_node, end_node):
        """Initialize a new event"""
        self.description = description
        # Type of an event discovery, combat, movement 
        self.event_type = event_type
        self.start_node = start_node
        self.end_node = end_node
    
    def to_dict(self):
        return {
            "description": self.description,
            "event_type": self.event_type,
            "start_node": self.start_node,
            "end_node": self.end_node
        }
    
    def __str__(self) -> str:
        """String representation of the event"""
        return self.description
    

    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        return cls(
            description=data["description"],
            event_type=data["event_type"],
            start_node=data["start_node"],
            end_node=data["end_node"]
        )


class EventManager:
    def __init__(self, json_path):
        self.json_path = Path(json_path)
        self.events = self._load_events()
        self.event_log = []

    def _load_events(self):
        if self.json_path.exists():
            with open(self.json_path, 'r') as f:
                return json.load(f)
        return {}

    def get_event(self, key):
        data = self.events.get(key)
        return Event.from_dict(data) if data else None

    def update_event(self, key, event):
        self.events[key] = event.to_dict()

    def save(self):
        with open(self.json_path, 'w') as f:
            json.dump(self.events, f, indent=2)
    
    def get_recent_events(self, count=5):
        return self.event_log[-count:]
    
    def get_events_by_type(self, event_type):
        return [event for event in self.event_log if event.event_type == event_type]
    
    def get_events_by_start_noode(self, start_node):
        return [event for event in self.event_log if event.start_node == start_node]
    
    def get_events_by_end_node(self, end_node):
        return [event for event in self.event_log if event.end_node == end_node]

    def log_event(self, event):
        self.event_log.append(event)