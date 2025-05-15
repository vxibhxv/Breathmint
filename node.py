import json
from typing import List, Any
import storage as st

class Connection:
    def __init__(self, node_a, node_b):
        self.node_a = node_a
        self.node_b = node_b
    
    
class GameNode:

    def __init__(self, info: dict[str, Any]):
        self.name = info['name']
        self.characters = info['characters']
        self.description = info['description']
        self.events = info['events']
        if 'current_event' in info:
            self.current_event = info['current_event']
        else:
            self.current_event = 0
        if 'visited_events' in info:
            self.visited_events = info['visited_events']
        else:
            self.visited_events = [0] * len(self.events)
        self.connections = info['connections']
        self.connection_list = self.build_connections(self.connections)
        self.items = info['items']
    
    def build_connections(self, connections):
        return [Connection(self.name, connection) for connection in connections]
    
    @classmethod
    def from_dict(cls, info: dict[str, Any]):
        return cls(info)

    def to_dict(self):
        return {
            "name": self.name,
            "characters": self.characters,
            "description": self.description,
            "events": self.events,
            "current_event": self.current_event,
            "visited_events": self.visited_events,
            "connections": self.connections,
            "items": self.items
        }

class GameNodeManager:
    def __init__(self, nodes, location):
        self.nodes = nodes
        self.node_log = self.build_node_log()
        self.current_node = self.get_node(location)
    
    def build_node_log(self):
        node_log = {}
        for node in self.nodes:
            node_dict = st.get_node(node)
            node_log[node] = GameNode.from_dict(node_dict)
        return node_log
    
    def get_node(self, location):
        node = None
        if location in self.node_log:
            node = self.node_log[location]
        else:
            node_dict = st.get_node(location)
            node = GameNode.from_dict(node_dict)
        self.log_node(node)
        return node

    def log_node(self, node: GameNode):
        self.current_node = node
        self.nodes.append(node.name)
        self.node_log[node.name] = node
    
    def current_node_events(self):
        return self.current_node.events
    
    def get_current_node_connections(self):
        return self.current_node.connection_list
    
    def move_to_node(self, node_name):
        self.current_node = self.node_log[node_name]
        return self.current_node
    
    def save(self):
        for node in self.nodes:
            n = self.node_log[node]
            st.save_node(n.name, n.to_dict())
        return self.nodes

# Test sample scenario for game node
# if __name__ == '__main__':
#     nodes = ['hotel_room', 'hotel_lobby', 'hotel', 'grocery_store']
#     node_manager = GameNodeManager(nodes, 'hotel')
#     connections = node_manager.get_current_node_connections()
#     print(connection.node_b.name for connection in connections)
#     print(node_manager.current_node.to_dict())
#     node_manager.save()
