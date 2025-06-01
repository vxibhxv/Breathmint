"""
Game State Management
Handles player state, current location, and game progression
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from core.exceptions import GameStateError
from game.storage import GameStorage

logger = logging.getLogger(__name__)

@dataclass
class Player:
    """Player data structure"""
    name: str
    health: int = 100
    max_health: int = 100
    inventory: List[str] = None
    stats: Dict[str, int] = None
    location: str = "hotel_room"
    relationships: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []
        if self.stats is None:
            self.stats = {"strength": 10, "intelligence": 10}
        if self.relationships is None:
            self.relationships = {}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create Player from dictionary"""
        return cls(
            name=data.get("name", "Unknown"),
            health=data.get("health", 100),
            max_health=data.get("max_health", 100),
            inventory=data.get("inventory", []),
            stats=data.get("stats", {"strength": 10, "intelligence": 10}),
            location=data.get("location", "hotel_room"),
            relationships=data.get("relationships", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Player to dictionary"""
        return {
            "name": self.name,
            "health": self.health,
            "max_health": self.max_health,
            "inventory": self.inventory.copy(),
            "stats": self.stats.copy(),
            "location": self.location,
            "relationships": self.relationships.copy()
        }

@dataclass
class GameNode:
    """Game location/node data structure"""
    name: str
    description: str
    characters: List[str] = None
    events: List[str] = None
    connections: List[str] = None
    items: List[str] = None
    current_event: Optional[str] = None
    
    def __post_init__(self):
        if self.characters is None:
            self.characters = []
        if self.events is None:
            self.events = []
        if self.connections is None:
            self.connections = []
        if self.items is None:
            self.items = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameNode':
        """Create GameNode from dictionary"""
        node = cls(
            name=data.get("name", "Unknown Location"),
            description=data.get("description", "A mysterious place."),
            characters=data.get("characters", []),
            events=data.get("events", []),
            connections=data.get("connections", []),
            items=data.get("items", []),
            current_event=data.get("current_event")
        )
        
        # Set current event from events list if not specified
        if not node.current_event and node.events:
            node.current_event = node.events[0]
        
        return node
    
    def describe(self) -> str:
        """Generate description of this location"""
        chars = ", ".join(self.characters) if self.characters else "no one"
        items = ", ".join(self.items) if self.items else "nothing interesting"
        conns = ", ".join(self.connections) if self.connections else "nowhere"
        
        description = f"Location: {self.name}\n"
        description += f"{self.description}\n"
        description += f"You see: {chars}.\n"
        description += f"Items here: {items}.\n"
        description += f"You can go to: {conns}."
        
        return description

@dataclass
class GameEvent:
    """Game event data structure"""
    name: str
    description: str
    event_type: str = "conversation"
    characters: List[str] = None
    start_node: str = ""
    end_node: str = ""
    consequence: List[str] = None
    
    def __post_init__(self):
        if self.characters is None:
            self.characters = []
        if self.consequence is None:
            self.consequence = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameEvent':
        """Create GameEvent from dictionary"""
        return cls(
            name=data.get("name", "Unknown Event"),
            description=data.get("description", "Something happens."),
            event_type=data.get("event_type", "conversation"),
            characters=data.get("characters", []),
            start_node=data.get("start_node", ""),
            end_node=data.get("end_node", ""),
            consequence=data.get("consequence", [])
        )
    
    def describe(self) -> str:
        """Generate description of this event"""
        chars = ", ".join(self.characters) if self.characters else "no one"
        return f"Event '{self.name}' ({self.event_type}): {self.description}\nInvolves: {chars}."

class GameState:
    """
    Main game state manager
    """
    
    def __init__(self, game_data: Dict[str, Any]):
        self.storage = GameStorage()
        self.turn_count = 0
        self.conversation_turns = 0
        self.locked_event = None
        self.in_combat = False
        
        # Load game data
        self._load_from_data(game_data)
    
    def _load_from_data(self, game_data: Dict[str, Any]):
        """Load game state from data dictionary"""
        try:
            # Load player
            player_name = game_data.get("player", "Tourist")
            player_data = self.storage.get_player(player_name)
            
            if player_data:
                self.player = Player.from_dict(player_data)
            else:
                # Create default player
                self.player = Player(name=player_name)
            
            # Load current node
            current_node_name = game_data.get("current_node", "hotel_room")
            node_data = self.storage.get_node(current_node_name)
            
            if node_data:
                self.current_node = GameNode.from_dict(node_data)
            else:
                # Create default node
                self.current_node = GameNode(
                    name=current_node_name,
                    description="You are in an unknown location.",
                    connections=[]
                )
            
            # Load current event if specified
            self.current_event = None
            if "current_event" in game_data:
                event_data = self.storage.get_event(game_data["current_event"])
                if event_data:
                    self.current_event = GameEvent.from_dict(event_data)
            elif self.current_node.current_event:
                event_data = self.storage.get_event(self.current_node.current_event)
                if event_data:
                    self.current_event = GameEvent.from_dict(event_data)
            
            # Load additional state
            self.conversation_turns = game_data.get("conversation_turns", 0)
            self.locked_event = game_data.get("locked_event")
            
            logger.info(f"Loaded game state: {self.player.name} at {self.current_node.name}")
            
        except Exception as e:
            logger.error(f"Error loading game state: {e}")
            raise GameStateError(f"Failed to load game state: {e}")
    
    def describe(self) -> str:
        """Generate description of current game state"""
        description = self.current_node.describe()
        
        if self.current_event:
            description += f"\n\nCurrent Event: {self.current_event.name}"
            description += f"\n{self.current_event.description}"
        
        return description
    
    def move_to(self, destination: str) -> bool:
        """
        Move player to new location
        
        Args:
            destination: Name of destination node
            
        Returns:
            True if move successful
        """
        try:
            # Check if destination is valid
            if destination not in self.current_node.connections:
                logger.warning(f"Cannot move to {destination} from {self.current_node.name}")
                return False
            
            # Load destination node
            node_data = self.storage.get_node(destination)
            if not node_data:
                logger.error(f"Destination node {destination} not found")
                return False
            
            # Move to new location
            self.current_node = GameNode.from_dict(node_data)
            self.player.location = destination
            
            # Check for new events
            if self.current_node.current_event:
                event_data = self.storage.get_event(self.current_node.current_event)
                if event_data:
                    self.current_event = GameEvent.from_dict(event_data)
                    self.conversation_turns = 0
                    self.locked_event = None
            
            self.turn_count += 1
            logger.info(f"Player moved to {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Error moving to {destination}: {e}")
            return False
    
    def perform_event(self) -> Any:
        """
        Perform current event
        
        Returns:
            Event result (varies by event type)
        """
        if not self.current_event:
            return "There's nothing special happening here."
        
        try:
            if self.current_event.event_type == "conversation":
                return self._handle_conversation()
            elif self.current_event.event_type == "movement":
                return self._handle_movement_event()
            elif self.current_event.event_type == "combat":
                return self._handle_combat_event()
            else:
                return f"Event type '{self.current_event.event_type}' not implemented."
                
        except Exception as e:
            logger.error(f"Error performing event {self.current_event.name}: {e}")
            return "Something went wrong with the event."
    
    def _handle_conversation(self) -> Dict[str, Any]:
        """Handle conversation events"""
        if not self.current_event.consequence:
            return {"response": "The conversation has no content."}
        
        # Simple conversation system - could be enhanced
        if self.conversation_turns < len(self.current_event.consequence):
            response = self.current_event.consequence[self.conversation_turns]
            self.conversation_turns += 1
            
            if self.conversation_turns >= len(self.current_event.consequence):
                # Conversation finished
                self.current_event = None
                self.locked_event = None
                return {
                    "status": "conversation_complete",
                    "response": response + "\n\n[Conversation ended]"
                }
            else:
                return {
                    "status": "awaiting_player_question",
                    "response": response
                }
        else:
            return {"response": "The conversation has ended."}
    
    def _handle_movement_event(self) -> Dict[str, Any]:
        """Handle movement events"""
        if self.current_event.end_node:
            if self.move_to(self.current_event.end_node):
                return {
                    "status": "movement_complete",
                    "location": self.current_event.end_node,
                    "description": self.current_node.describe()
                }
        
        return {"response": "Movement event failed."}
    
    def _handle_combat_event(self) -> Dict[str, Any]:
        """Handle combat events"""
        # Placeholder for combat system
        return {"response": "Combat system not yet implemented."}
    
    def save_game(self) -> bool:
        """Save current game state"""
        try:
            return self.storage.save_game_state(self)
        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            return False
    
    def add_item(self, item: str):
        """Add item to player inventory"""
        if item not in self.player.inventory:
            self.player.inventory.append(item)
            logger.info(f"Added {item} to inventory")
    
    def remove_item(self, item: str) -> bool:
        """Remove item from player inventory"""
        if item in self.player.inventory:
            self.player.inventory.remove(item)
            logger.info(f"Removed {item} from inventory")
            return True
        return False
    
    def has_item(self, item: str) -> bool:
        """Check if player has item"""
        return item in self.player.inventory
    
    def get_available_actions(self) -> List[str]:
        """Get list of available actions"""
        actions = ["look", "inventory"]
        
        if self.current_node.connections:
            actions.extend([f"go to {conn}" for conn in self.current_node.connections])
        
        if self.current_event:
            actions.append("continue event")
        
        if self.current_node.items:
            actions.extend([f"take {item}" for item in self.current_node.items])
        
        return actions
    
    def respond(self, response: str):
        """Add response to chat history (for frontend integration)"""
        # This method exists for compatibility with the frontend
        # Could be expanded to maintain chat history
        pass