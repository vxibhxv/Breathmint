from game_ai import GameAI
from state import GameState
import storage as st
import json

# Setup
ai = GameAI()

data = st.get_game("Tourist")
state = GameState(data)

print(state.describe())

while True:
    user_input = input("\n> ")
    if state.locked_event == "conversation":
        # Don't classify — treat everything as part of the event
        classified = { "action": "perform_event", "args": { "raw": user_input } }
    else:
        # Normal classification
        classified = ai.classify_input(user_input, state)

    response = ai.process_command(classified, state)
    state.respond(response)

    if classified["action"] == "quit":
        print(response)
        break

    print(response)
