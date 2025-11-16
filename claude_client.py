"""Claude API client with conversation management."""
import logging
from typing import Dict, List, Optional
from anthropic import Anthropic
from config import Config

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages conversation contexts for users."""
    
    def __init__(self):
        """Initialize the conversation manager."""
        self.conversations: Dict[int, List[Dict[str, str]]] = {}
    
    def get_context(self, user_id: int) -> List[Dict[str, str]]:
        """Get conversation context for a user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            List of message dictionaries
        """
        return self.conversations.get(user_id, [])
    
    def add_message(self, user_id: int, role: str, content: str) -> None:
        """Add a message to user's conversation context.
        
        Args:
            user_id: Telegram user ID
            role: Message role (user or assistant)
            content: Message content
        """
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        self.conversations[user_id].append({
            "role": role,
            "content": content
        })
        
        logger.info(f"Added {role} message for user {user_id}. Context size: {len(self.conversations[user_id])}")
    
    def clear_context(self, user_id: int) -> None:
        """Clear conversation context for a user.
        
        Args:
            user_id: Telegram user ID
        """
        if user_id in self.conversations:
            context_size = len(self.conversations[user_id])
            del self.conversations[user_id]
            logger.info(f"Cleared context for user {user_id}. Removed {context_size} messages")
    
    def get_context_size(self, user_id: int) -> int:
        """Get the number of messages in user's context.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Number of messages in context
        """
        return len(self.conversations.get(user_id, []))


class ClaudeClient:
    """Client for interacting with Claude API."""
    
    def __init__(self):
        """Initialize the Claude client."""
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.conversation_manager = ConversationManager()
        logger.info(f"Initialized Claude client with model: {Config.CLAUDE_MODEL}")
    
    async def send_message(self, user_id: int, message: str) -> str:
        """Send a message to Claude and get response.
        
        Args:
            user_id: Telegram user ID
            message: User's message
            
        Returns:
            Claude's response text
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Add user message to context
            self.conversation_manager.add_message(user_id, "user", message)
            
            # Get full conversation context
            messages = self.conversation_manager.get_context(user_id)
            
            logger.info(f"Sending message to Claude for user {user_id}. Context size: {len(messages)}")
            
            # Call Claude API
            response = self.client.messages.create(
                model=Config.CLAUDE_MODEL,
                max_tokens=Config.MAX_TOKENS,
                messages=messages
            )
            
            # Extract response text
            response_text = response.content[0].text
            
            # Add assistant response to context
            self.conversation_manager.add_message(user_id, "assistant", response_text)
            
            logger.info(f"Received response from Claude for user {user_id}")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error calling Claude API for user {user_id}: {e}")
            raise
    
    def clear_context(self, user_id: int) -> None:
        """Clear conversation context for a user.
        
        Args:
            user_id: Telegram user ID
        """
        self.conversation_manager.clear_context(user_id)
    
    def get_context_size(self, user_id: int) -> int:
        """Get the number of messages in user's context.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Number of messages in context
        """
        return self.conversation_manager.get_context_size(user_id)

