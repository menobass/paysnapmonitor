
from fastapi import FastAPI
from app.db import db
from app.config import config
from app.logging_utils import setup_logger
from app.dashboard import dashboard_router
from app.bot import HiveBot
import threading

app = FastAPI()
logger = setup_logger()
bot = HiveBot()

def start_bot():
    bot.poll_blocks()

@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=start_bot, daemon=True)
    thread.start()

app.include_router(dashboard_router, prefix="/admin")

@app.get("/")
def root():
    return {"status": "Pay n Snap Hive Cashback Bot is running."}
