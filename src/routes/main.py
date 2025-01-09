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
# Set webhook URL
if not os.environ.get("WEBHOOK_URL"):
    print("Please expose WEBHOOK_URL environment variable!")
    exit()
    
@app.on_event("startup")
async def on_startup():
    # Run the Telegram bot in the background
    # background_tasks = BackgroundTasks()
    # background_tasks.add_task(application.run_polling)
    await telegram_handler.init_bot()
    # pass
@app.route(f'/{os.environ.get("TELEGRAM_TOKEN")}', methods=['POST'])
@telegram_handler.verify_webhook_token
@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    return await telegram_handler.telegram_webhook_call(request)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Chat Agent!"}
