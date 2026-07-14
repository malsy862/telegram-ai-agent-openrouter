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

# Model yang masih aktif per Juli 2026
MODEL = "llama-3.3-70b-versatile"

# Database permanen
Base = declarative_base()
engine = create_engine('sqlite:///bot_memory.db')
Session =​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​
