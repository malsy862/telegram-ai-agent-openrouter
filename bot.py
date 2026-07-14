import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from openai import OpenAI
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# ================== GROQ ==================
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# Model yang masih aktif
MODEL = "llama3-70b-8192"

# Database permanen
Base = declarative_base()
engine = create_engine('sqlite:///bot_memory.db')
Session = sessionmaker(bind=engine)

class Ingatan(Base):
    __tablename__ = 'ingatan'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    role = Column(String)
    pesan = Column(Text)

Base.metadata.create_all(engine)

# ================== BOT ==================
async def start(update: Update, context):
    await update.message.reply_text("✅ Bot Groq Llama3 70B aktif!\nTanya apa saja ya 😊")

async def balas(update: Update, context):
    user_id = update.effective_user.id
    teks = update.message.text

    await update.message.reply​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​
