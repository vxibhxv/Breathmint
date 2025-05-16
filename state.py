from typing import List, Dict, Any
import os, json
import time
import node, player, event
import storage as st

class GameState:
    def __init__(self, data: dict[str, Any]):
        self.player = player.Player.from_name(data['player'])
        if 'current_node' not in data:
            data['current_node'] = self.player.location
        self.node_manager = node.GameNodeManager(data['node_log'], data['current_node'])
        self.event_manager = event.EventManager(data['event_log'])
        self.current_node = self.node_manager.current_node
        if 'current_event' in data:
            self.current_event = self.event_manager.get_event(data['current_event'])
        else:
            self.current_event = self.event_manager.get_current_event()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to dictionary for saving"""
        c_e = self.current_event.name if self.current_event else None
        op = {
            "player": self.player.name,
            "event_log": self.event_manager.save(),
            "node_log": self.node_manager.save(),
            "current_node": self.current_node.name
        }
        if c_e:
            op['current_event'] = c_e

        return op
    
    def save_game(self):
       """Save game state to file"""
       st.save_game(self.player.name, self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """Create game state from dictionary data"""
        # data['player'] = st.load_player(data['player'])
        return cls(data)
    
    def find_nodes(self):
        nds = self.node_manager.get_current_node_connections()
        options = []
        for n in nds:
            noe = self.node_manager.get_node(n)
            options.append(noe.to_context())
        return options

    def visit_event(self, event, event_stage):
        
        self.current_event = event
        cns = self.event_manager.visit_event(event, event_stage)
        self.current_node.visit_event(event, cns['complete'])
        if cns['type'] == "conversation":
            print("Consequence of the action was a conversation type")
            print(cns['prose'], "\n ------- \n")
    
    def take_action(self, inp):
        if len(inp) == 2:
            self.visit_event(inp['event'], inp['stage'])
        else:
            new_node = self.node_manager.get_node(inp['node'])
            print("Entering new node:", new_node.name)
            print("\n", new_node.description, "\n ------- \n")
            self.current_node = new_node
            self.current_event = None
    
    def find_options(self):
        events = self.current_node.find_available_events()
        options = []
        for event in events:
            event_obj = self.event_manager.get_event(event)
            options.append(event_obj.to_context())
        return options
    
    def find_and_validate_options(self):
        print("Finding options")
        options = self.find_options()
        if len(options) == 0:
            print("No events available, moving to connecting node")
            options = self.find_nodes()
            
        print(options, "\n ------- \n")
        return options



        
if __name__ == '__main__':
    game_dict = {
        "player": "Tourist",
        "event_log": [],
        "node_log": [],
        "current_node": "bar",
        "current_event": "pink_conversation"
    }
    gs = GameState(game_dict)
    #TODO get event name
    
    

    #while count:
    gs.find_options()
    eve = input("What event you want to do?\n---> ")
    print("You entered:", eve)
    user_input = input("What stage you want to do?\n---> ")
    print("You entered:", user_input)
    gs.visit_event(eve, user_input)
    gs.find_available_stages()
