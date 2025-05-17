from typing import Any, List, Dict
import state
import interface
import storage as st
import json

class GameEngine:
    def __init__(self, info: dict[str, Any]):
        self.game_state = state.GameState(info)
        with open('api_key.txt', 'r') as f:
            api_key = f.read().strip()

        self.ai = interface.Interface(self.game_state, api_key)
    
    def options(self, ops):
        need_input = []
        for op in ops:
            for k,v in op.items():
                print("Need input of type: ", k)
                if k not in need_input:
                    need_input.append(k)
        return need_input
    
    def map_input(self, input_req, options):
        # Ai parses input to input_req
        # Returns a list of inputs mapped to input_req
        print(input_req)
        print(options)
        eve = input("What do you want to do?\n---> ")
        print("You entered:", eve)
        intent, args = self.ai.handle_input(eve, input_req, options)
        return intent, args
        
    def map_output(self, intent, args):
        if intent == "where_am_i":
            print(self.game_state.current_node.description)
        elif intent == "who_is_here":
            print(self.game_state.current_node.characters)
        elif intent == "move_location" or intent == "sub_action":
            for k, v in args.items():
                if v == "unknown":
                    print("Unknown input, please try again")
                    return
            self.game_state.take_action(args)
        elif intent == "where_can_i_go":
            print(self.game_state.current_node.connections)
        elif intent == "what_can_i_do":
            print(self.game_state.current_node.events)
        elif intent == "save":
            print("Save the game")
        elif intent == "quit":
            print("Quit the game")
        elif intent == "fallback":
            print("Unknown / ambiguous input")
        else:
            print("Unknown intent")
        


    def game_loop(self):
        count = 1

        while count:
            ops = self.game_state.find_and_validate_options()
            input_req = self.options(ops)
            print(input_req, len(input_req))
            intent, args = self.map_input(input_req, ops)
            self.map_output(intent, args)          

if __name__ == '__main__':
    player_info = st._load_dict("players.json")
    print(player_info)
    print(type(player_info))
    # player = input("Choose player: ")
    # print("You entered:", player)
    player = "Tourist"
    game_dict = st.get_game(player)

    ge = GameEngine(game_dict)
    ge.game_loop()
