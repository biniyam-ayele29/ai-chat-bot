import os 
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, Application
from fastapi import Request, HTTPException
from src.utils.llmLangChain import LLMLangchainBanking
from src.utils.utils import Utils
from typing import Callable, Any
from functools import wraps
from fastapi import Request as request, Response as response

class TelegramHandler:
    def __init__(self) -> any:
        # Telegram bot setup
        if not os.environ.get("OPENAI_API_KEY"):
            print("Please expose OPENAI_API_KEY environment variable!")
            exit()
        if not os.environ.get("TELEGRAM_BOT_TOKEN"):
            print("Please expose TELEGRAM_BOT_TOKEN environment variable!")
            exit()
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.webhook_url = os.getenv("WEBHOOK_URL")
        self.application = None
        import sqlite3
        print(dir(sqlite3.Connection))
        # self.application.initialize()
        # # Register command and message handlers
        # self.application.add_handler(CommandHandler("start", self.start_command))
        # self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.utils = Utils()
        self.logger = self.utils.get_logger()
        try:
            self.bot = Bot(token=self.telegram_bot_token)
        except Exception as e:
            self.logger.error(f"Failed to initialize Telegram bot: {str(e)}")
            raise

    async def handle_message(self, update: Update, context: CallbackContext):
        question = update.message.text
        # Use the trained banking model to get a response
        llm_langchain_banking = LLMLangchainBanking()
        await update.message.reply_text(llm_langchain_banking.run([question]))

    async def telegram_webhook_call(self, request: Request):
        try:
            json_data = await request.json()
            update = Update.de_json(json_data, self.application.bot)
            await self.application.process_update(update)
            return {"status": "ok"}
        except Exception as e:
            self.logger.error(f"An error occurred while processing your request. {e}")  
            return response('OK', status_code=200)
        
    async def init_bot(self) -> None:
        """Initialize the bot and set up webhook"""
        try:
            # Verify bot token is valid
            self.application = await self.setup_application()
            bot_info = await self.application.bot.get_me()
            self.logger.info(f"Bot initialized: @{bot_info.username}")
                
        except Exception as e:
            self.logger.error(f"Bot initialization failed: {str(e)}")
            raise

    def verify_webhook_token(self, func: Callable) -> Callable:
        """Decorator to verify webhook requests"""
        @wraps(func)
        def wrapped(*args, **kwargs) -> Any:
            if 'X-Telegram-Bot-Api-Secret-Token' not in request.headers:
                return response('Unauthorized', status=403)
            
            if request.headers['X-Telegram-Bot-Api-Secret-Token'] != self.telegram_bot_token:
                return response('Unauthorized', status=403)

            return func(*args, **kwargs)
        return wrapped

    async def setup_webhook(self) -> bool:
        """Setup webhook for the bot"""
        try:
            webhook_url = f"{self.webhook_url}"
            # Set webhook
            await self.application.bot.set_webhook(url=webhook_url)
            self.logger.info("Webhook setup successful")
            return True
        except Exception as e:
            self.logger.error(f"Error setting up webhook: {str(e)}")
            return False


    async def setup_application(self) -> Application:
        """Initialize and setup the application"""
        global application
        
        # Create application instance
        application = (
            Application.builder()
            .token(self.telegram_bot_token)
            .build()
        )
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Initialize the application
        await application.initialize()
        
        # Set webhook
        webhook_url = f"{self.webhook_url}"
        await application.bot.set_webhook(url=webhook_url)
        
        # Start application
        await application.start()
        self.logger.info("Application initialized and webhook set")
        return application

    async def start_command(self, update: Update, context: CallbackContext) -> None:
        """Handle /start command"""
        try:
            if update.message:
                first_name = update.message.from_user.first_name
                welcome_message = f"Hello {first_name},\nWelcome to the Oromia Bank assistant bot! How can I help you today?"
                await update.message.reply_text(welcome_message)
            else:
                await update.message.reply_text(
                    "Welcome to the Oromia Bank assistant bot! How can I help you today?"
                )
        except Exception as e:
            self.logger.error(f"Error in start command: {str(e)}")
