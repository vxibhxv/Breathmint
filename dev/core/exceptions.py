"""
Custom exceptions for the Power Rangers game engine
"""

class GameError(Exception):
    """Base exception for game-related errors"""
    pass

class AIError(GameError):
    """Base exception for AI-related errors"""
    pass

class AIUnavailableError(AIError):
    """Raised when AI service is unavailable"""
    pass

class AIRateLimitError(AIError):
    """Raised when AI service rate limit is exceeded"""
    pass

class AIInvalidRequestError(AIError):
    """Raised when AI request is invalid"""
    pass

class GameStateError(GameError):
    """Raised when game state is invalid"""
    pass

class StorageError(GameError):
    """Raised when storage operations fail"""
    pass

class CombatError(GameError):
    """Raised when combat operations fail"""
    pass

class ConfigurationError(GameError):
    """Raised when configuration is invalid"""
    pass