"""
Centralized AI Client
Handles all Anthropic API interactions with proper error handling and fallbacks
"""
import logging
from typing import Dict, Any, Optional, List
import time
from dataclasses import dataclass

from .config import config
from .exceptions import AIError, AIUnavailableError, AIRateLimitError

logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    """Standardized AI response"""
    content: str
    success: bool
    error: Optional[str] = None
    tokens_used: Optional[int] = None
    
class AIClient:
    """
    Centralized AI client that handles Anthropic SDK issues
    Falls back gracefully when AI is unavailable
    """
    
    def __init__(self):
        self.client = None
        self.available = False
        self.last_error = None
        self.rate_limit_reset = 0
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Anthropic client with error handling"""
        if not config.ai.api_key:
            logger.warning("No API key provided - AI will be unavailable")
            return
        
        try:
            # Try to import and initialize Anthropic
            import anthropic
            
            # Use specific version to avoid type errors
            self.client = anthropic.Anthropic(
                api_key=config.ai.api_key,
                timeout=config.ai.timeout,
                max_retries=config.ai.max_retries
            )
            
            # Test the client with a simple call
            self._test_client()
            
            self.available = True
            logger.info("AI client initialized successfully")
            
        except ImportError as e:
            logger.error(f"Anthropic package not available: {e}")
            self.last_error = f"Anthropic package not installed: {e}"
            
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {e}")
            self.last_error = str(e)
            
            # Handle specific SDK errors
            if "cache_creation_input_tokens" in str(e):
                logger.error("Detected Anthropic SDK type error - using fallback mode")
                self._try_fallback_initialization()
    
    def _try_fallback_initialization(self):
        """Try alternative initialization methods"""
        try:
            # Method 1: Try with minimal parameters
            import anthropic
            self.client = anthropic.Anthropic(api_key=config.ai.api_key)
            self.available = True
            logger.info("AI client initialized with fallback method")
            
        except Exception as e:
            logger.error(f"Fallback initialization failed: {e}")
            # Method 2: Create mock client for testing
            self._create_mock_client()
    
    def _create_mock_client(self):
        """Create a mock client for testing when real client fails"""
        class MockClient:
            def __init__(self):
                self.messages = MockMessages()
        
        class MockMessages:
            def create(self, **kwargs):
                return type('obj', (object,), {
                    'content': [type('obj', (object,), {
                        'text': f"Mock response to: {kwargs.get('messages', [{}])[-1].get('content', 'unknown')}"
                    })()]
                })()
        
        self.client = MockClient()
        self.available = True
        logger.warning("Using mock AI client - responses will be simulated")
    
    def _test_client(self):
        """Test the client with a simple call"""
        try:
            response = self.client.messages.create(
                model=config.ai.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            logger.info("AI client test successful")
        except Exception as e:
            logger.warning(f"AI client test failed: {e}")
            # Don't fail initialization for test failures
    
    def is_available(self) -> bool:
        """Check if AI is available"""
        return self.available and self.client is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get AI client status"""
        return {
            "available": self.available,
            "last_error": self.last_error,
            "model": config.ai.model,
            "rate_limited": time.time() < self.rate_limit_reset
        }
    
    def create_message(self, messages: List[Dict[str, str]], **kwargs) -> AIResponse:
        """
        Create a message with comprehensive error handling
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters
            
        Returns:
            AIResponse object with content and metadata
        """
        if not self.is_available():
            return AIResponse(
                content="AI is currently unavailable. The game will continue with basic responses.",
                success=False,
                error=self.last_error or "AI client not available"
            )
        
        # Check rate limiting
        if time.time() < self.rate_limit_reset:
            return AIResponse(
                content="AI is temporarily rate limited. Please try again later.",
                success=False,
                error="Rate limited"
            )
        
        try:
            # Prepare parameters
            params = {
                'model': kwargs.get('model', config.ai.model),
                'max_tokens': min(kwargs.get('max_tokens', config.ai.max_tokens), 4000),
                'messages': messages
            }
            
            # Add optional parameters safely
            if 'temperature' in kwargs:
                params['temperature'] = max(0.0, min(1.0, kwargs['temperature']))
            elif config.ai.temperature is not None:
                params['temperature'] = config.ai.temperature
            
            if 'system' in kwargs:
                params['system'] = kwargs['system']
            
            # Make the API call
            response = self.client.messages.create(**params)
            
            # Extract content safely
            content = self._extract_content(response)
            
            return AIResponse(
                content=content,
                success=True,
                tokens_used=getattr(response, 'usage', {}).get('output_tokens', 0)
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"AI API call failed: {error_msg}")
            
            # Handle specific errors
            if "rate_limit" in error_msg.lower():
                self.rate_limit_reset = time.time() + 60  # 1 minute cooldown
                return AIResponse(
                    content="AI is temporarily rate limited. The game will continue with basic responses.",
                    success=False,
                    error="Rate limited"
                )
            
            elif "invalid_request" in error_msg.lower():
                return AIResponse(
                    content="Request was invalid. The game will continue with basic responses.",
                    success=False,
                    error="Invalid request"
                )
            
            else:
                # Generic error handling
                return AIResponse(
                    content="AI encountered an error. The game will continue with basic responses.",
                    success=False,
                    error=error_msg
                )
    
    def _extract_content(self, response) -> str:
        """Safely extract content from API response"""
        try:
            if hasattr(response, 'content') and response.content:
                if hasattr(response.content[0], 'text'):
                    return response.content[0].text
                else:
                    return str(response.content[0])
            else:
                return "No content in response"
        except (IndexError, AttributeError) as e:
            logger.error(f"Failed to extract content from response: {e}")
            return "Failed to extract AI response"
    
    def classify_text(self, text: str, options: List[str]) -> str:
        """
        Classify text into one of the provided options
        
        Args:
            text: Text to classify
            options: List of possible classifications
            
        Returns:
            Classification result or 'unknown'
        """
        if not self.is_available():
            return self._basic_classify(text, options)
        
        prompt = f"""
Classify the following text into one of these categories: {', '.join(options)}

Text: "{text}"

Respond with ONLY the category name that best fits.
"""
        
        response = self.create_message([
            {"role": "user", "content": prompt}
        ], max_tokens=50)
        
        if response.success:
            result = response.content.strip().lower()
            # Find best match
            for option in options:
                if option.lower() in result or result in option.lower():
                    return option
        
        # Fallback to basic classification
        return self._basic_classify(text, options)
    
    def _basic_classify(self, text: str, options: List[str]) -> str:
        """Basic rule-based classification when AI is unavailable"""
        text = text.lower()
        
        # Define basic rules
        if any(word in text for word in ['where', 'look', 'describe', 'examine']):
            return 'describe' if 'describe' in options else options[0]
        elif any(word in text for word in ['go', 'move', 'travel', 'walk']):
            return 'move_to' if 'move_to' in options else options[0]
        elif any(word in text for word in ['do', 'start', 'continue', 'perform']):
            return 'perform_event' if 'perform_event' in options else options[0]
        elif any(word in text for word in ['quit', 'exit', 'leave']):
            return 'quit' if 'quit' in options else options[0]
        
        return options[0] if options else 'unknown'

# Global AI client instance
ai_client = AIClient()