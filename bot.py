import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from openai import OpenAI
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

load_dotenv()

# ================== GROQ ==================
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = "llama-3.1-70b-versatile"   # bagus & cepat

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
    await update.message.reply_text("✅ Bot Groq Llama 3.1 70B aktif!\nTanya apa saja ya 😊")

async def balas(update: Update, context):
    user_id = update.effective_user.id
    teks = update.message.text

    session = Session()
    lama = session.query(Ingatan).filter_by(user_id=user_id).all()
    history = [{"role": x.role, "content": x.pesan} for x in lama]
    history.append({"role": "user", "content": teks})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=history[-20:],
            temperature=0.7,
            max_tokens=800,
        )
        jawaban = response.choices[0].message.content
    except Exception as e:
        print(f"Groq Error: {e}")
        jawaban = "Maaf, sedang sibuk. Coba lagi ya."

    # Simpan permanen
    session.add(Ingatan(user_id=user_id, role="user", pesan=teks))
    session.add(Ingatan(user_id=user_id, role="assistant", pesan=jawaban))
    session.commit()
    session.close()

    await update.message.reply_text(jawaban)

# ================== JALANKAN ==================
if __name__ == "__main__":
    TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("❌ Token Telegram tidak ditemukan!")
        exit(1)

    print("🤖 Bot Groq sedang jalan...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, balas))
    
    app.run_polling()
