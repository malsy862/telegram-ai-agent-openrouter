import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler
import openai
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

load_dotenv()

# ================== PENGATURAN ==================
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = os.getenv("OPENROUTER_API_KEY")

# Model gratis terbaik
MODEL = "tencent/hy3:free"

# Ambil token dengan fleksibel (bisa TELEGRAM_TOKEN atau BOT_TOKEN)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")

if not TELEGRAM_TOKEN:
    print("❌ ERROR: TELEGRAM_TOKEN atau BOT_TOKEN tidak ditemukan di Variables Railway!")
    exit(1)

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
    await update.message.reply_text("✅ Bot Tencent Hy3 aktif!\nSilakan tanya apa saja 😊")

async def balas(update: Update, context):
    user_id = update.effective_user.id
    teks = update.message.text

    session = Session()

    lama = session.query(Ingatan).filter_by(user_id=user_id).all()
    history = [{"role": x.role, "content": x.pesan} for x in lama]
    history.append({"role": "user", "content": teks})

    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=history[-20:],
            temperature=0.7,
        )
        jawaban = response.choices[0].message.content
    except Exception as e:
        jawaban = "Maaf, sedang ada masalah. Coba lagi ya."

    # Simpan permanen
    session.add(Ingatan(user_id=user_id, role="user", pesan=teks))
    session.add(Ingatan(user_id=user_id, role="assistant", pesan=jawaban))
    session.commit()
    session.close()

    await update.message.reply_text(jawaban)

# ================== JALANKAN BOT ==================
if __name__ == "__main__":
    print("🤖 Bot sedang starting...")
    print(f"Model: {MODEL}")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, balas))
    
    print("✅ Bot berhasil jalan!")
    app.run_polling()
