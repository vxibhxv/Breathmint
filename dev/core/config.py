"""
Core Configuration Module
Handles all configuration including API keys and environment settings
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIConfig:
    """AI-specific configuration"""
    api_key: Optional[str] = None
    model: str = "claude-3-haiku-20240307"
    max_tokens: int = 1000
    temperature: float = 0.1
    timeout: float = 30.0
    max_retries: int = 2

@dataclass
class GameConfig:
    """Game-specific configuration"""
    default_player: str = "Tourist"
    default_location: str = "hotel_room"
    save_interval: int = 30  # seconds
    max_chat_history: int = 100

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.logs_dir = self.base_dir / "logs"
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Load configurations
        self.ai = self._load_ai_config()
        self.game = self._load_game_config()
        
        # Validate configuration
        self._validate()
    
    def _load_ai_config(self) -> AIConfig:
        """Load AI configuration from environment and defaults"""
        return AIConfig(
            api_key=self._get_api_key(),
            model=os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307"),
            max_tokens=int(os.getenv("MAX_TOKENS", "1000")),
            temperature=float(os.getenv("TEMPERATURE", "0.1")),
            timeout=float(os.getenv("AI_TIMEOUT", "30.0")),
            max_retries=int(os.getenv("AI_MAX_RETRIES", "2"))
        )
    
    def _load_game_config(self) -> GameConfig:
        """Load game configuration"""
        return GameConfig(
            default_player=os.getenv("DEFAULT_PLAYER", "Tourist"),
            default_location=os.getenv("DEFAULT_LOCATION", "hotel_room"),
            save_interval=int(os.getenv("SAVE_INTERVAL", "30")),
            max_chat_history=int(os.getenv("MAX_CHAT_HISTORY", "100"))
        )
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from multiple sources with priority"""
        # Priority order: ENV variable, .env file, hardcoded fallback
        
        # 1. Environment variable
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            logger.info("API key loaded from environment variable")
            return api_key
        
        # 2. .env file
        env_file = self.base_dir / ".env"
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith("ANTHROPIC_API_KEY="):
                            api_key = line.split("=", 1)[1].strip()
                            if api_key:
                                logger.info("API key loaded from .env file")
                                return api_key
            except Exception as e:
                logger.warning(f"Failed to read .env file: {e}")
        
        # 3. Hardcoded fallback (from your original code)
        fallback_key = "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"
        logger.warning("Using hardcoded API key - set ANTHROPIC_API_KEY environment variable for production")
        return fallback_key
    
    def _validate(self):
        """Validate configuration"""
        issues = []
        
        if not self.ai.api_key:
            issues.append("No Anthropic API key found")
        
        if not self.data_dir.exists():
            issues.append(f"Data directory not found: {self.data_dir}")
        
        if issues:
            logger.warning("Configuration issues found:")
            for issue in issues:
                logger.warning(f"  - {issue}")
    
    def is_ai_enabled(self) -> bool:
        """Check if AI functionality is enabled"""
        return bool(self.ai.api_key)
    
    def get_data_file(self, filename: str) -> Path:
        """Get path to data file"""
        return self.data_dir / filename
    
    def get_safe_dict(self) -> Dict[str, Any]:
        """Get configuration as dict without sensitive data"""
        return {
            "ai_enabled": self.is_ai_enabled(),
            "ai_model": self.ai.model,
            "max_tokens": self.ai.max_tokens,
            "default_player": self.game.default_player,
            "default_location": self.game.default_location,
            "data_dir": str(self.data_dir),
        }

# Global configuration instance
config = Config()