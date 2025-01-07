
import os
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
from fastapi import Request, HTTPException
from langchain.schema import HumanMessage, SystemMessage
from src.utils.llmLangChain import LLMLangchainBanking

class TelegramHandler:
    def __init__(self):
        # Telegram bot setup
        if not os.environ.get("OPENAI_API_KEY"):
            print("Please expose OPENAI_API_KEY environment variable!")
            exit()
        if not os.environ.get("TELEGRAM_BOT_TOKEN"):
            print("Please expose TELEGRAM_BOT_TOKEN environment variable!")
            exit()
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.application = Application.builder().token(self.telegram_bot_token).build()
        # Register command and message handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))


    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Welcome to the Oromia Bank assistant bot! How can I help you today?")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        question = update.message.text
        # Use the trained banking model to get a response
        llm_langchain_banking = LLMLangchainBanking()
        await update.message.reply_text(llm_langchain_banking.run([question]))

    async def run_telegram_bot(self):
        self.application.run_polling()

    async def telegram_webhook_call(self, request: Request):
        try:
            update = Update.de_json(await request.json(), self.application.bot)
            await self.handle_message(update, self.application)
            return {"status": "ok"}
        except Exception as e:
            return {"error": "An error occurred while processing your request. Please try again later."} 