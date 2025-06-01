"""
Game Storage System
Handles all data persistence for the Power Rangers game
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from core.config import config
from core.exceptions import StorageError

logger = logging.getLogger(__name__)

class GameStorage:
    """
    Centralized storage system for game data
    """
    
    def __init__(self):
        self.data_dir = config.data_dir
        self.ensure_data_files()
    
    def ensure_data_files(self):
        """Ensure all required data files exist"""
        default_files = {
            'nodes.json': {},
            'events.json': {},
            'players.json': {},
            'saves.json': {},
            'characters.json': {}
        }
        
        for filename, default_content in default_files.items():
            file_path = self.data_dir / filename
            if not file_path.exists():
                self.save_json(filename, default_content)
                logger.info(f"Created default {filename}")
    
    def load_json(self, filename: str) -> Dict[str, Any]:
        """
        Load JSON data from file
        
        Args:
            filename: Name of JSON file to load
            
        Returns:
            Dictionary of loaded data
        """
        try:
            file_path = self.data_dir / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"File {filename} not found, returning empty dict")
                return {}
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            raise StorageError(f"Failed to load {filename}: {e}")
    
    def save_json(self, filename: str, data: Dict[str, Any]):
        """
        Save data to JSON file
        
        Args:
            filename: Name of JSON file to save
            data: Data to save
        """
        try:
            file_path = self.data_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved {filename}")
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")
            raise StorageError(f"Failed to save {filename}: {e}")
    
    def load_nodes(self) -> Dict[str, Any]:
        """Load all game nodes"""
        return self.load_json('nodes.json')
    
    def load_events(self) -> Dict[str, Any]:
        """Load all game events"""
        return self.load_json('events.json')
    
    def load_players(self) -> Dict[str, Any]:
        """Load all player data"""
        return self.load_json('players.json')
    
    def load_saves(self) -> Dict[str, Any]:
        """Load all save games"""
        return self.load_json('saves.json')
    
    def get_node(self, node_name: str) -> Optional[Dict[str, Any]]:
        """Get specific node data"""
        nodes = self.load_nodes()
        return nodes.get(node_name)
    
    def get_event(self, event_name: str) -> Optional[Dict[str, Any]]:
        """Get specific event data"""
        events = self.load_events()
        return events.get(event_name)
    
    def get_player(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Get specific player data"""
        players = self.load_players()
        return players.get(player_name)
    
    def get_game(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Get saved game for player"""
        saves = self.load_saves()
        return saves.get(player_name)
    
    def save_game_state(self, game_state) -> bool:
        """
        Save current game state
        
        Args:
            game_state: GameState object to save
            
        Returns:
            True if saved successfully
        """
        try:
            saves = self.load_saves()
            
            # Convert game state to saveable format
            save_data = {
                "player": game_state.player.name,
                "current_node": game_state.current_node.name,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            # Add optional fields if they exist
            if hasattr(game_state, 'current_event') and game_state.current_event:
                save_data["current_event"] = game_state.current_event.name
            
            if hasattr(game_state, 'conversation_turns'):
                save_data["conversation_turns"] = game_state.conversation_turns
            
            if hasattr(game_state, 'locked_event'):
                save_data["locked_event"] = game_state.locked_event
            
            # Save to saves file
            saves[game_state.player.name] = save_data
            self.save_json('saves.json', saves)
            
            logger.info(f"Saved game for {game_state.player.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save game state: {e}")
            return False
    
    def load_game_state(self, player_name: str):
        """
        Load game state for player
        
        Args:
            player_name: Name of player to load
            
        Returns:
            GameState object or None if not found
        """
        try:
            save_data = self.get_game(player_name)
            if save_data:
                from game.state import GameState
                return GameState(save_data)
            return None
        except Exception as e:
            logger.error(f"Failed to load game state for {player_name}: {e}")
            return None
    
    def create_new_game(self, player_name: str):
        """
        Create new game state for player
        
        Args:
            player_name: Name of new player
            
        Returns:
            New GameState object
        """
        try:
            from game.state import GameState
            
            # Create default game data
            game_data = {
                "player": player_name,
                "current_node": config.game.default_location,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            return GameState(game_data)
            
        except Exception as e:
            logger.error(f"Failed to create new game for {player_name}: {e}")
            raise StorageError(f"Failed to create new game: {e}")
    
    def initialize_data_files(self):
        """Initialize data files if they don't exist (compatibility)"""
        self.ensure_data_files()
    
    def get_data_file_path(self, filename: str) -> Path:
        """Get path to data file"""
        return self.data_dir / filename