"""
Improved Game Engine for Power Rangers: Neo Seoul
Clean, modular design with proper error handling
"""
import sys
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.config import config
from core.ai_client import ai_client
from core.exceptions import GameError, GameStateError
from game.ai_handler import AIHandler
from game.state import GameState
from game.storage import GameStorage

logger = logging.getLogger(__name__)

class GameEngine:
    """
    Main game engine with improved architecture
    """
    
    def __init__(self):
        self.ai_handler = None
        self.state = None
        self.storage = None
        self.running = False
        
        # Initialize systems
        self._initialize_systems()
    
    def _initialize_systems(self):
        """Initialize all game systems"""
        try:
            # Initialize storage system
            self.storage = GameStorage()
            logger.info("Storage system initialized")
            
            # Initialize AI handler
            self.ai_handler = AIHandler()
            logger.info("AI handler initialized")
            
            logger.info("Game engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize game systems: {e}")
            raise GameError(f"Game initialization failed: {e}")
    
    def start_game(self, player_name: str = None) -> bool:
        """
        Start a new game or load existing game
        
        Args:
            player_name: Name of player to load/create
            
        Returns:
            True if game started successfully
        """
        try:
            # Use default player if none specified
            if not player_name:
                player_name = config.game.default_player
            
            # Load or create game state
            self.state = self.storage.load_game_state(player_name)
            if not self.state:
                self.state = self.storage.create_new_game(player_name)
                logger.info(f"Created new game for {player_name}")
            else:
                logger.info(f"Loaded existing game for {player_name}")
            
            self.running = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to start game: {e}")
            return False
    
    def process_input(self, user_input: str) -> str:
        """
        Process user input and return game response
        
        Args:
            user_input: User's text input
            
        Returns:
            Game response as string
        """
        if not self.running or not self.state:
            return "Game is not running. Please start a new game."
        
        try:
            # Clean and validate input
            user_input = user_input.strip()
            if not user_input:
                return "Please enter a command."
            
            # Check for special commands first
            special_response = self._handle_special_commands(user_input)
            if special_response:
                return special_response
            
            # Process through AI handler
            classified_input = self.ai_handler.classify_input(user_input, self.state)
            response = self.ai_handler.process_command(classified_input, self.state)
            
            # Auto-save periodically
            self._auto_save()
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing input '{user_input}': {e}")
            return f"Sorry, I couldn't process that command. Please try again. ({str(e)[:50]})"
    
    def _handle_special_commands(self, user_input: str) -> Optional[str]:
        """
        Handle special engine commands
        
        Args:
            user_input: User input to check
            
        Returns:
            Response string if special command handled, None otherwise
        """
        cmd = user_input.lower().strip()
        
        # Quit commands
        if cmd in ['quit', 'exit', 'q']:
            self.save_game()
            self.running = False
            return "Game saved. Goodbye!"
        
        # Save command
        elif cmd == 'save':
            if self.save_game():
                return "Game saved successfully!"
            else:
                return "Failed to save game."
        
        # Help command
        elif cmd in ['help', 'h']:
            return self._get_help_text()
        
        # Status command
        elif cmd == 'status':
            return self._get_status_text()
        
        # AI status command
        elif cmd == 'ai_status':
            return self._get_ai_status_text()
        
        # Debug command (if enabled)
        elif cmd == 'debug' and config.ai.model == "claude-3-haiku-20240307":  # Dev mode check
            return self._get_debug_text()
        
        return None
    
    def _get_help_text(self) -> str:
        """Generate help text"""
        help_text = """
=== POWER RANGERS: NEO SEOUL HELP ===

Basic Commands:
• look, describe - Look around your current location
• go to [location] - Move to a different location  
• do [action] - Perform an action or start an event
• inventory - Check your items
• talk to [character] - Start a conversation

System Commands:
• save - Save your game
• status - Show player status
• help - Show this help text
• quit - Save and exit the game

AI Status: {}
""".format("ONLINE" if ai_client.is_available() else "OFFLINE (basic mode)")
        
        return help_text.strip()
    
    def _get_status_text(self) -> str:
        """Generate status text"""
        if not self.state:
            return "No game loaded."
        
        status = f"""
=== PLAYER STATUS ===
Name: {self.state.player.name}
Health: {self.state.player.health}/{self.state.player.max_health}
Location: {self.state.current_node.name}
Items: {', '.join(self.state.player.inventory) if self.state.player.inventory else 'None'}
"""
        
        if hasattr(self.state, 'current_event') and self.state.current_event:
            status += f"Current Event: {self.state.current_event.name}\n"
        
        return status.strip()
    
    def _get_ai_status_text(self) -> str:
        """Generate AI status text"""
        ai_status = ai_client.get_status()
        return f"""
=== AI STATUS ===
Available: {ai_status['available']}
Model: {ai_status['model']}
Rate Limited: {ai_status['rate_limited']}
Last Error: {ai_status['last_error'] or 'None'}
"""
    
    def _get_debug_text(self) -> str:
        """Generate debug text"""
        if not self.state:
            return "No game state loaded."
        
        debug_info = f"""
=== DEBUG INFO ===
Player: {self.state.player.name}
Current Node: {self.state.current_node.name}
Available Connections: {self.state.current_node.connections}
Current Event: {getattr(self.state, 'current_event', None)}
AI Available: {ai_client.is_available()}
Storage Path: {self.storage.data_dir}
"""
        return debug_info.strip()
    
    def save_game(self) -> bool:
        """
        Save current game state
        
        Returns:
            True if saved successfully
        """
        try:
            if self.state and self.storage:
                self.storage.save_game_state(self.state)
                logger.info("Game saved successfully")
                return True
            else:
                logger.warning("Cannot save - no game state or storage")
                return False
        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            return False
    
    def _auto_save(self):
        """Auto-save game periodically"""
        # Simple implementation - could be enhanced with timers
        if self.state and hasattr(self.state, 'turn_count'):
            if self.state.turn_count % 5 == 0:  # Save every 5 turns
                self.save_game()
    
    def get_game_info(self) -> Dict[str, Any]:
        """
        Get current game information
        
        Returns:
            Dictionary with game info
        """
        if not self.state:
            return {"status": "no_game_loaded"}
        
        return {
            "status": "running" if self.running else "stopped",
            "player": self.state.player.name,
            "location": self.state.current_node.name,
            "health": f"{self.state.player.health}/{self.state.player.max_health}",
            "ai_available": ai_client.is_available(),
            "connections": self.state.current_node.connections,
            "items": self.state.player.inventory,
            "current_event": getattr(self.state, 'current_event', None)
        }
    
    def shutdown(self):
        """Shutdown the game engine"""
        if self.running:
            self.save_game()
            self.running = False
        logger.info("Game engine shutdown")

def main():
    """Main entry point for command-line play"""
    try:
        # Create game engine
        engine = GameEngine()
        
        # Start game
        print("=== POWER RANGERS: NEO SEOUL ===")
        print("Initializing game...")
        
        if not engine.start_game():
            print("Failed to start game.")
            return
        
        print("Game started successfully!")
        print("Type 'help' for commands, 'quit' to exit.\n")
        
        # Initial game description
        initial_response = engine.process_input("look")
        print(initial_response)
        
        # Main game loop
        while engine.running:
            try:
                user_input = input("\n> ").strip()
                if not user_input:
                    continue
                    
                response = engine.process_input(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\nGame interrupted. Saving...")
                engine.save_game()
                break
            except EOFError:
                print("\nGoodbye!")
                engine.save_game()
                break
                
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)
    
    finally:
        if 'engine' in locals():
            engine.shutdown()

if __name__ == "__main__":
    main()