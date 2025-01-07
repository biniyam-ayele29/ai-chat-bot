from fastapi import FastAPI, Request, BackgroundTasks
from langchain.schema import HumanMessage, SystemMessage
from src.utils.llmLangChain import LLMLangchainBanking
from src.model.requests import Query
import os, re
from src.controller.telegramHandler import TelegramHandler
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes



app = FastAPI()

telegram_handler = TelegramHandler()

application = ApplicationBuilder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()

# Register command and message handlers
application.add_handler(CommandHandler("start", telegram_handler.start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_handler.handle_message))
# Set webhook URL
if not os.environ.get("WEBHOOK_URL"):
    print("Please expose WEBHOOK_URL environment variable!")
    exit()
application.bot.set_webhook(url=os.environ.get("WEBHOOK_URL"))
    
@app.on_event("startup")
async def on_startup():
    # Run the Telegram bot in the background
    background_tasks = BackgroundTasks()
    background_tasks.add_task(application.run_polling)

@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    return await telegram_handler.telegram_webhook_call(request)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Chat Agent!"}
