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
        if type(self.event_stages) != list:
            self.event_stages = self.event_stages[0]
        self.characters=data["characters"],
        self.start_node=data["start_node"],
        self.end_node=data["end_node"],
        self.consequence=data["consequence"],
        if type(self.consequence) != list:
            self.consequence = self.consequence[0]
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
    
    def visit_stage(self, stage):
        if type(self.event_stages) != list:
            self.event_stages = self.event_stages[0]
        i = self.event_stages.index(stage)
        self.current_stage = i
        self.visited_stages[i] = 1
        uv = self.find_unvisited_stages()
        complete = False
        if len(uv) == 0:
            complete = True
        cns = {}
        if type(self.event_type) != str:
            self.event_type = self.event_type[0]
        cns['type'] = self.event_type

        if cns['type'] == "conversation":
            tmp = [self.consequence[i*2], self.consequence[i*2+1]]
            cns['prose'] = tmp
        cns['complete'] = complete
        return cns
    
    def find_unvisited_stages(self):
        unvisited = []
        for i, stage in enumerate(self.event_stages):
            if self.visited_stages[i] == 0:
                unvisited.append(stage)
        return unvisited
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        return cls(data)
    
    def to_context(self):
        cont = {
            "event": self.name,
            "stages": self.find_unvisited_stages()
        }
        return cont


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
    
    def add_event(self, event_name):
        event_dict = st.get_event(event_name)
        self.event_log[event_name] = Event.from_dict(event_dict)
        self.events.append(event_name)

    def get_event(self, event):
        if event not in self.events:
            self.add_event(event)
        return self.event_log[event]

    def get_current_event(self):
        if len(self.events) == 0:
            return None
        return self.get_event(self.events[-1])
    
    def visit_event(self, event, event_stage):
        event_obj = self.event_log[event]
        return event_obj.visit_stage(event_stage)
    
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