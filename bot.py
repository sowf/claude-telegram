"""Telegram bot that proxies requests to Claude API."""
import logging
import sys
from typing import Optional
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from config import Config
from claude_client import ClaudeClient

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)


class TelegramClaudeBot:
    """Telegram bot that acts as a proxy to Claude API."""
    
    def __init__(self):
        """Initialize the bot."""
        self.claude_client = ClaudeClient()
        self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
        logger.info("Bot initialized successfully")
    
    def _setup_handlers(self) -> None:
        """Setup command and message handlers."""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("clear", self.clear_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        logger.info("Handlers registered")
    
    def _is_authorized(self, update: Update) -> bool:
        """Check if user is authorized to use the bot.
        
        Args:
            update: Telegram update object
            
        Returns:
            True if user is authorized, False otherwise
        """
        username = update.effective_user.username
        
        if not username:
            logger.warning(f"User {update.effective_user.id} has no username")
            return False
        
        is_authorized = username.lower() in Config.ALLOWED_USERNAMES
        
        if not is_authorized:
            logger.warning(f"Unauthorized access attempt by @{username} (ID: {update.effective_user.id})")
        
        return is_authorized
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command.
        
        Args:
            update: Telegram update object
            context: Callback context
        """
        if not self._is_authorized(update):
            await update.message.reply_text(
                "❌ У вас нет доступа к этому боту.\n"
                "Access denied. You are not authorized to use this bot."
            )
            return
        
        user = update.effective_user
        logger.info(f"User @{user.username} (ID: {user.id}) started the bot")
        
        welcome_message = (
            f"👋 Привет, {user.first_name}!\n\n"
            "Я бот-прокси для Claude API. Просто отправьте мне любое сообщение, "
            "и я передам его Claude для обработки.\n\n"
            "📝 Доступные команды:\n"
            "/start - Начать работу\n"
            "/clear - Очистить контекст разговора\n"
            "/help - Показать справку\n\n"
            f"🤖 Модель: {Config.CLAUDE_MODEL}\n"
            "✨ Я запоминаю контекст вашего разговора для более естественного общения."
        )
        
        await update.message.reply_text(welcome_message)
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /clear command.
        
        Args:
            update: Telegram update object
            context: Callback context
        """
        if not self._is_authorized(update):
            await update.message.reply_text(
                "❌ У вас нет доступа к этому боту.\n"
                "Access denied."
            )
            return
        
        user_id = update.effective_user.id
        context_size = self.claude_client.get_context_size(user_id)
        self.claude_client.clear_context(user_id)
        
        logger.info(f"User @{update.effective_user.username} (ID: {user_id}) cleared context")
        
        await update.message.reply_text(
            f"🧹 Контекст очищен!\n"
            f"Удалено сообщений: {context_size}\n\n"
            "Можете начать новый разговор."
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command.
        
        Args:
            update: Telegram update object
            context: Callback context
        """
        if not self._is_authorized(update):
            await update.message.reply_text("❌ Access denied.")
            return
        
        help_message = (
            "📖 Справка по использованию бота\n\n"
            "🤖 Этот бот является прокси для Claude API от Anthropic.\n\n"
            "💬 Как использовать:\n"
            "Просто отправьте любое текстовое сообщение, и я перешлю его Claude. "
            "Бот запоминает историю вашего разговора для более естественного общения.\n\n"
            "📝 Команды:\n"
            "/start - Начать работу с ботом\n"
            "/clear - Очистить историю разговора и начать заново\n"
            "/help - Показать эту справку\n\n"
            f"⚙️ Настройки:\n"
            f"Модель: {Config.CLAUDE_MODEL}\n"
            f"Максимум токенов: {Config.MAX_TOKENS}\n\n"
            "💡 Советы:\n"
            "- Используйте /clear, если хотите начать новую тему\n"
            "- Контекст разговора сохраняется между сообщениями\n"
            "- Бот работает только с текстовыми сообщениями"
        )
        
        await update.message.reply_text(help_message)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages.
        
        Args:
            update: Telegram update object
            context: Callback context
        """
        if not self._is_authorized(update):
            await update.message.reply_text("❌ Access denied.")
            return
        
        user = update.effective_user
        user_message = update.message.text
        
        logger.info(f"Received message from @{user.username} (ID: {user.id}): {user_message[:50]}...")
        
        # Send typing action
        await update.message.chat.send_action(action="typing")
        
        try:
            # Send message to Claude
            response = await self.claude_client.send_message(user.id, user_message)
            
            # Send response to user
            # Split long messages if needed (Telegram limit is 4096 chars)
            if len(response) <= 4096:
                await update.message.reply_text(response)
            else:
                # Split message into chunks
                chunks = [response[i:i+4096] for i in range(0, len(response), 4096)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            
            logger.info(f"Sent response to @{user.username} (ID: {user.id})")
            
        except Exception as e:
            error_message = (
                "❌ Произошла ошибка при обработке вашего сообщения.\n"
                "An error occurred while processing your message.\n\n"
                f"Ошибка: {str(e)}"
            )
            await update.message.reply_text(error_message)
            logger.error(f"Error processing message from user {user.id}: {e}", exc_info=True)
    
    def run(self) -> None:
        """Start the bot."""
        logger.info("Starting bot...")
        logger.info(f"Allowed usernames: {', '.join(f'@{u}' for u in Config.ALLOWED_USERNAMES)}")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point."""
    try:
        bot = TelegramClaudeBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

