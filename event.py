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
        self.name=data["name"],
        self.description=data["description"],
        self.event_type=data["event_type"],
        self.event_stages=data["event_stages"],
        self.characters=data["characters"],
        self.start_node=data["start_node"],
        self.end_node=data["end_node"],
        self.consequence=data["consequence"],
        self.current_stage = 0
        if "current_stage" in data:
            self.current_stage = data["current_stage"]
        self.visited_stages = [0] * len(self.event_stages)
        if "visited_stages" in data:
            self.visited_stages=data["visited_stages"]
    
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "event_type": self.event_type,
            "event_stages": self.event_stages,
            "characters": self.characters,
            "start_node": self.start_node,
            "end_node": self.end_node,
            "current_stage": self.current_stage,
            "visited_stages": self.visited_stages,
            "consequence": self.consequence
        }
    
    def __str__(self) -> str:
        """String representation of the event"""
        return self.name
    
    def mark_stage_visited(self):
        self.visited_stage[self.current_stage] = 1
    
    def find_unvisited_stages(self):
        unvisited = []
        for i, stage in enumerate(self.event_stages):
            if self.visited_stage[i] == 0:
                unvisited.append(stage)
        return unvisited
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        return cls(data)


class EventManager:
    def __init__(self, events):
        self.events = events
        self.event_log = self.build_event_log()
    
    def build_event_log(self):
        event_log = {}
        for event in self.events:
            event_dict = st.get_event(event)
            event_log[event] = Event.from_dict(event_dict)
        return event_log
    
    def add_event(self, event):
        event_dict = st.get_event(event)
        self.log_event(Event.from_dict(event_dict))
    
    def get_event(self, event):
        if event not in self.events:
            print("Event not found")
            return
        return self.event_log[event]

    def get_current_event(self):
        if len(self.events) == 0:
            return None
        return self.get_event(self.events[-1])

    
    def get_recent_events(self, count=5):
        return [self.event_log[event] for event in self.events[-count:]]
    
    def get_events_by_type(self, event_type):
        # TODO: filter by type
        pass
        # return [event for event in self.event_log if event.event_type == event_type]
    
    def get_events_by_start_noode(self, start_node):
        # TODO: filter by start node
        pass
        # return [event for event in self.event_log if event.start_node == start_node]
    
    def get_events_by_end_node(self, end_node):
        # TODO: filter by end node
        pass
        # return [event for event in self.event_log if event.end_node == end_node]

    def log_event(self, event):
        self.event_log[event.name] = event
        self.events.append(event.name)
    
    def get_consequence(self, event_name, event_stage):
        event = self.event_log[event_name]
        event.current_stage = event_stage
        event.mark_stage_visited()
        return event.consequence[event_stage]
    
    def save(self):
        for event in self.events:
            e = self.event_log[event]
            st.save_event(e.name, e.to_dict())
        return self.events

# # Test sample scenario for event manager
# if __name__ == "__main__":
#     events = ['waking_up', 'number_convo']
#     event_manager = EventManager(events)
#     import pdb; pdb.set_trace()