#!/usr/bin/env python3
"""Configuration checker for Claude Telegram Bot."""
import os
import sys
from pathlib import Path


def print_status(check_name: str, passed: bool, message: str = "") -> None:
    """Print status of a check."""
    status = "✓" if passed else "✗"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} {check_name}", end="")
    if message:
        print(f": {message}")
    else:
        print()


def check_env_file() -> bool:
    """Check if .env file exists."""
    return Path(".env").exists()


def check_env_variables() -> dict:
    """Check required environment variables."""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
        "ALLOWED_USERNAMES": os.getenv("ALLOWED_USERNAMES", ""),
    }
    
    optional_vars = {
        "CLAUDE_MODEL": os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
        "MAX_TOKENS": os.getenv("MAX_TOKENS", "4096"),
    }
    
    return {"required": required_vars, "optional": optional_vars}


def check_dependencies() -> dict:
    """Check if required packages are installed."""
    packages = {}
    
    try:
        import telegram
        packages["python-telegram-bot"] = telegram.__version__
    except ImportError:
        packages["python-telegram-bot"] = None
    
    try:
        import anthropic
        packages["anthropic"] = anthropic.__version__
    except ImportError:
        packages["anthropic"] = None
    
    try:
        import dotenv
        packages["python-dotenv"] = dotenv.__version__
    except ImportError:
        packages["python-dotenv"] = None
    
    return packages


def main():
    """Run configuration checks."""
    print("\n" + "="*60)
    print("  Claude Telegram Bot - Configuration Checker")
    print("="*60 + "\n")
    
    all_passed = True
    
    # Check .env file
    print("📄 Checking .env file...")
    env_exists = check_env_file()
    print_status(".env file exists", env_exists)
    
    if not env_exists:
        print("\n⚠️  .env file not found!")
        print("   Create it from .env.example:")
        print("   cp .env.example .env")
        all_passed = False
    
    print()
    
    # Check dependencies
    print("📦 Checking dependencies...")
    packages = check_dependencies()
    for package, version in packages.items():
        if version:
            print_status(f"{package}", True, f"v{version}")
        else:
            print_status(f"{package}", False, "NOT INSTALLED")
            all_passed = False
    
    if not all(packages.values()):
        print("\n⚠️  Some dependencies are missing!")
        print("   Install them with:")
        print("   pip install -r requirements.txt")
    
    print()
    
    # Check environment variables
    if env_exists:
        print("🔑 Checking environment variables...")
        try:
            env_vars = check_env_variables()
            
            # Check required variables
            for var, value in env_vars["required"].items():
                is_set = bool(value and value != f"your_{var.lower()}_here")
                
                if is_set:
                    # Mask sensitive data
                    if "TOKEN" in var or "KEY" in var:
                        masked_value = value[:10] + "..." if len(value) > 10 else "***"
                        print_status(var, True, masked_value)
                    else:
                        print_status(var, True, value)
                else:
                    print_status(var, False, "NOT SET or using example value")
                    all_passed = False
            
            print()
            
            # Check optional variables
            print("⚙️  Optional settings:")
            for var, value in env_vars["optional"].items():
                print(f"  • {var}: {value}")
            
        except Exception as e:
            print_status("Environment check", False, str(e))
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("✅ All checks passed! You're ready to run the bot.")
        print("\n🚀 Start the bot with:")
        print("   python bot.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)
    
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

