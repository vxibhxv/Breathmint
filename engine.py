from typing import Any, List, Dict
import state
import storage as st
import json

class GameEngine:
    def __init__(self, info: dict[str, Any]):
        self.game_state = state.GameState(info)

        self.ai = "hero"
    
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
        


    def game_loop(self):
        count = 1

        while count:
            ops = self.game_state.find_and_validate_options()
            input_req = self.options(ops)
            print(input_req, len(input_req))
            inputs = self.map_input(input_req, ops)            
            self.game_state.take_action(inputs)

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
