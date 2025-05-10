"""
Event class for text adventure game.
This module handles game events and event tracking.
"""
from typing import List, Dict, Any, Optional
import datetime


class Event:
    """
    Class representing a single game event
    """
    def __init__(self, description: str, event_type: str = "general"):
        """Initialize a new event"""
        self.description = description
        self.event_type = event_type  # E.g., "movement", "combat", "discovery"
        self.timestamp = datetime.datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for saving"""
        return {
            "description": self.description,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create an event from dictionary data"""
        event = cls(
            description=data.get("description", "Unknown event"),
            event_type=data.get("event_type", "general")
        )
        
        # Convert timestamp string back to datetime if it exists
        timestamp_str = data.get("timestamp")
        if timestamp_str:
            try:
                event.timestamp = datetime.datetime.fromisoformat(timestamp_str)
            except ValueError:
                # If timestamp can't be parsed, use current time
                event.timestamp = datetime.datetime.now()
        
        return event
    
    def __str__(self) -> str:
        """String representation of the event"""
        return self.description


class EventLog:
    """
    Class for tracking and managing game events
    """
    def __init__(self):
        """Initialize an empty event log"""
        self.events: List[Event] = []
    
    def add_event(self, event: Event) -> None:
        """Add an event to the log"""
        self.events.append(event)
    
    def add_event_description(self, description: str, event_type: str = "general") -> None:
        """Create and add a new event from a description"""
        event = Event(description, event_type)
        self.add_event(event)
    
    def get_recent_events(self, count: int = 5) -> List[Event]:
        """Get the most recent events"""
        return self.events[-count:] if self.events else []
    
    def get_events_by_type(self, event_type: str) -> List[Event]:
        """Get events of a specific type"""
        return [event for event in self.events if event.event_type == event_type]
    
    def clear(self) -> None:
        """Clear all events"""
        self.events = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event log to dictionary for saving"""
        return {
            "events": [event.to_dict() for event in self.events]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventLog':
        """Create an event log from dictionary data"""
        log = cls()
        events_data = data.get("events", [])
        for event_data in events_data:
            log.add_event(Event.from_dict(event_data))
        return log