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

def get_event_detail(event_id):
    event_list = _load_dict("event_list.json")
    return event_list.get(event_id)

def save_event_detail(event_id, event_data):
    event_list = _load_dict("event_list.json")
    event_list[event_id] = event_data
    _save_dict("event_list.json", event_list)

def get_location(loc_id):
    locations = _load_dict("loc_list.json")
    return locations.get(loc_id)

def save_location(loc_id, loc_data):
    locations = _load_dict("loc_list.json")
    locations[loc_id] = loc_data
    _save_dict("loc_list.json", locations)

def get_node(node_id):
    nodes = _load_dict("nodes.json")
    return nodes.get(node_id)

def save_node(node_id, node_data):
    nodes = _load_dict("nodes.json")
    nodes[node_id] = node_data
    _save_dict("nodes.json", nodes)
