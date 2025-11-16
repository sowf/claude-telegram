"""Configuration module for the Telegram bot."""
import os
from typing import Set
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for bot settings."""
    
    # Telegram settings
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Anthropic settings
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4096"))
    
    # Access control
    ALLOWED_USERNAMES: Set[str] = set(
        username.strip().lower()
        for username in os.getenv("ALLOWED_USERNAMES", "").split(",")
        if username.strip()
    )
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required")
        
        if not cls.ALLOWED_USERNAMES:
            raise ValueError("ALLOWED_USERNAMES is required")


# Validate config on import
Config.validate()

