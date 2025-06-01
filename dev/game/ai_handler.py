"""
AI Handler - Interface between game logic and AI client
Handles all AI-related game functionality with fallbacks
"""
import logging
import difflib
from typing import Dict, Any, List, Optional

from core.ai_client import ai_client
from core.config import config
from core.exceptions import AIError

logger = logging.getLogger(__name__)

class AIHandler:
    """
    Handles AI integration for the game with robust fallbacks
    """
    
    def __init__(self):
        self.classification_options = [
            "describe",
            "move_to", 
            "perform_event",
            "inventory",
            "combat",
            "save",
            "quit"
        ]
    
    def classify_input(self, user_input: str, game_state) -> Dict[str, Any]:
        """
        Classify user input into actionable commands
        
        Args:
            user_input: Raw user input
            game_state: Current game state
            
        Returns:
            Dictionary with action and arguments
        """
        try:
            # First try rule-based classification (fast and reliable)
            rule_result = self._rule_based_classify(user_input)
            if rule_result:
                return self._build_classification(rule_result, user_input)
            
            # If AI is available, use it for more complex cases
            if ai_client.is_available():
                ai_result = self._ai_classify(user_input)
                if ai_result:
                    return self._build_classification(ai_result, user_input)
            
            # Fallback to basic classification
            return self._build_classification("describe", user_input)
            
        except Exception as e:
            logger.error(f"Error classifying input '{user_input}': {e}")
            return self._build_classification("describe", user_input)
    
    def _rule_based_classify(self, text: str) -> Optional[str]:
        """
        Rule-based classification for common patterns
        
        Args:
            text: Input text to classify
            
        Returns:
            Classification or None if no match
        """
        text = text.lower().strip()
        
        # Quit/Save commands
        if any(word in text for word in ['quit', 'exit', 'bye', 'goodbye']):
            return "quit"
        if 'save' in text:
            return "save"
        
        # Movement commands
        if any(phrase in text for phrase in ['go to', 'move to', 'travel to', 'walk to', 'head to']):
            return "move_to"
        if any(word in text for word in ['go', 'move', 'travel', 'walk', 'head']) and any(word in text for word in ['north', 'south', 'east', 'west', 'up', 'down']):
            return "move_to"
        
        # Description commands
        if any(word in text for word in ['look', 'examine', 'describe', 'where', 'what']):
            return "describe"
        
        # Action commands
        if any(phrase in text for phrase in ['talk to', 'speak to', 'chat with']):
            return "perform_event"
        if any(word in text for word in ['do', 'start', 'continue', 'perform', 'use', 'take', 'get']):
            return "perform_event"
        
        # Inventory commands
        if any(word in text for word in ['inventory', 'items', 'backpack', 'bag']):
            return "inventory"
        
        # Combat commands
        if any(word in text for word in ['fight', 'attack', 'combat', 'battle']):
            return "combat"
        
        return None
    
    def _ai_classify(self, text: str) -> Optional[str]:
        """
        AI-based classification for complex cases
        
        Args:
            text: Input text to classify
            
        Returns:
            Classification or None if AI fails
        """
        try:
            prompt = f"""
Classify this game command into one category: {', '.join(self.classification_options)}

Command: "{text}"

Rules:
- "describe" for looking around, examining, getting information
- "move_to" for going somewhere, traveling, movement
- "perform_event" for doing actions, talking, interacting
- "inventory" for checking items
- "combat" for fighting, attacking
- "save" for saving game
- "quit" for exiting

Respond with ONLY the category name.
"""
            
            response = ai_client.create_message([
                {"role": "user", "content": prompt}
            ], max_tokens=20)
            
            if response.success:
                result = response.content.strip().lower()
                # Find best match from options
                for option in self.classification_options:
                    if option.lower() in result:
                        return option
            
        except Exception as e:
            logger.error(f"AI classification failed: {e}")
        
        return None
    
    def _build_classification(self, action: str, raw_input: str) -> Dict[str, Any]:
        """
        Build classification result dictionary
        
        Args:
            action: Classified action
            raw_input: Original user input
            
        Returns:
            Classification dictionary
        """
        return {
            "action": action,
            "raw": raw_input,
            "confidence": "high" if action != "describe" else "medium"
        }
    
    def process_command(self, classified: Dict[str, Any], game_state) -> str:
        """
        Process classified command and return response
        
        Args:
            classified: Classified command from classify_input
            game_state: Current game state
            
        Returns:
            Game response string
        """
        action = classified["action"]
        raw_input = classified["raw"]
        
        try:
            # Route to appropriate handler
            if action == "describe":
                return self._handle_describe(raw_input, game_state)
            elif action == "move_to":
                return self._handle_movement(raw_input, game_state)
            elif action == "perform_event":
                return self._handle_event(raw_input, game_state)
            elif action == "inventory":
                return self._handle_inventory(game_state)
            elif action == "combat":
                return self._handle_combat(raw_input, game_state)
            elif action == "save":
                return "Game will be saved."
            elif action == "quit":
                return "Goodbye!"
            else:
                return f"I don't understand '{raw_input}'. Type 'help' for available commands."
                
        except Exception as e:
            logger.error(f"Error processing command {action}: {e}")
            return f"Sorry, I couldn't process that command. Please try again."
    
    def _handle_describe(self, raw_input: str, game_state) -> str:
        """Handle description requests"""
        try:
            # Get basic description
            base_description = game_state.describe()
            
            # If AI is available and user asked a specific question, enhance it
            if ai_client.is_available() and any(word in raw_input.lower() for word in ['what', 'who', 'why', 'how']):
                enhanced = self._enhance_description(raw_input, base_description)
                if enhanced:
                    return enhanced
            
            return base_description
            
        except Exception as e:
            logger.error(f"Error handling describe: {e}")
            return game_state.describe() if hasattr(game_state, 'describe') else "You look around."
    
    def _handle_movement(self, raw_input: str, game_state) -> str:
        """Handle movement commands"""
        try:
            # Extract destination
            destination = self._extract_destination(raw_input, game_state.current_node.connections)
            
            if destination and destination in game_state.current_node.connections:
                if game_state.move_to(destination):
                    # Generate movement response
                    if ai_client.is_available():
                        return self._generate_movement_response(destination, game_state)
                    else:
                        return f"You move to {destination}.\n\n{game_state.describe()}"
                else:
                    return f"You can't go to {destination} right now."
            else:
                available = ", ".join(game_state.current_node.connections)
                return f"You can't go there. Available locations: {available}"
                
        except Exception as e:
            logger.error(f"Error handling movement: {e}")
            return "I couldn't understand where you want to go."
    
    def _handle_event(self, raw_input: str, game_state) -> str:
        """Handle event/action commands"""
        try:
            # Check if there's a current event
            if hasattr(game_state, 'current_event') and game_state.current_event:
                result = game_state.perform_event()
                
                # Handle different result types
                if isinstance(result, dict):
                    if result.get("status") == "awaiting_player_question":
                        return result["response"]
                    elif result.get("status") == "movement_complete":
                        return f"You are now at {result['location']}.\n\n{result['description']}"
                    else:
                        return result.get("response", str(result))
                else:
                    return str(result)
            else:
                return "There's nothing special to do here right now."
                
        except Exception as e:
            logger.error(f"Error handling event: {e}")
            return "I couldn't perform that action."
    
    def _handle_inventory(self, game_state) -> str:
        """Handle inventory commands"""
        try:
            if hasattr(game_state.player, 'inventory') and game_state.player.inventory:
                items = ", ".join(game_state.player.inventory)
                return f"You are carrying: {items}"
            else:
                return "You are not carrying anything."
        except Exception as e:
            logger.error(f"Error handling inventory: {e}")
            return "I couldn't check your inventory."
    
    def _handle_combat(self, raw_input: str, game_state) -> str:
        """Handle combat commands"""
        try:
            # This would integrate with the combat system
            return "Combat system is not currently available."
        except Exception as e:
            logger.error(f"Error handling combat: {e}")
            return "Combat is not available right now."
    
    def _extract_destination(self, text: str, available_locations: List[str]) -> Optional[str]:
        """
        Extract destination from movement command
        
        Args:
            text: User input text
            available_locations: List of available destinations
            
        Returns:
            Best matching destination or None
        """
        text_lower = text.lower()
        
        # Direct matches first
        for location in available_locations:
            if location.lower() in text_lower:
                return location
        
        # Fuzzy matching
        words = text_lower.split()
        for word in words:
            matches = difflib.get_close_matches(word, [loc.lower() for loc in available_locations], n=1, cutoff=0.6)
            if matches:
                # Return original case version
                for location in available_locations:
                    if location.lower() == matches[0]:
                        return location
        
        return None
    
    def _enhance_description(self, question: str, base_description: str) -> Optional[str]:
        """
        Enhance description using AI for specific questions
        
        Args:
            question: User's question
            base_description: Base game description
            
        Returns:
            Enhanced description or None
        """
        try:
            prompt = f"""
You are narrating a text adventure game. The player asked: "{question}"

Current game context:
```
{base_description}
```

Provide a brief, immersive response based only on the context provided. Stay in character as the game narrator.
"""
            
            response = ai_client.create_message([
                {"role": "user", "content": prompt}
            ], max_tokens=200)
            
            if response.success:
                return response.content
                
        except Exception as e:
            logger.error(f"Error enhancing description: {e}")
        
        return None
    
    def _generate_movement_response(self, destination: str, game_state) -> str:
        """
        Generate enhanced movement response using AI
        
        Args:
            destination: Where the player moved
            game_state: Current game state
            
        Returns:
            Movement response
        """
        try:
            prompt = f"""
The player just moved to {destination}. Write a brief transition describing the movement and what they see.

New location:
```
{game_state.describe()}
```

Keep it concise and atmospheric.
"""
            
            response = ai_client.create_message([
                {"role": "user", "content": prompt}
            ], max_tokens=150)
            
            if response.success:
                return response.content
            else:
                return f"You move to {destination}.\n\n{game_state.describe()}"
                
        except Exception as e:
            logger.error(f"Error generating movement response: {e}")
            return f"You move to {destination}.\n\n{game_state.describe()}"