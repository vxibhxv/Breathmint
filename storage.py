import os
import json

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True) 

def _get_path(filename):
    return os.path.join(DATA_DIR, filename)

def _load_dict(filename):
    path = _get_path(filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def _save_dict(filename, data):
    path = _get_path(filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def get_player(player_id):
    players = _load_dict("players.json")
    return players.get(player_id)

def save_player(player_id, player_data):
    players = _load_dict("players.json")
    players[player_id] = player_data
    _save_dict("players.json", players)

def get_character(character_id):
    characters = _load_dict("characters.json")
    return characters.get(character_id)

def save_character(character_id, char_data):
    characters = _load_dict("characters.json")
    characters[character_id] = char_data
    _save_dict("characters.json", characters)

def get_event(event_id):
    events = _load_dict("events.json")
    return events.get(event_id)

def save_event(event_id, event_data):
    events = _load_dict("events.json")
    events[event_id] = event_data
    _save_dict("events.json", events)

def get_node(node_id):
    nodes = _load_dict("nodes.json")
    return nodes.get(node_id)

def save_node(node_id, node_data):
    nodes = _load_dict("nodes.json")
    nodes[node_id] = node_data
    _save_dict("nodes.json", nodes)

def save_game(player_id, game_data):
    games = _load_dict("saves.json")
    games[player_id] = game_data
    _save_dict("saves.json", games)

def get_game(player_id):
    games = _load_dict("saves.json")
    return games.get(player_id)

