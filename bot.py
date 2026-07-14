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

# Database permanen
Base = declarative_base()
engine = create_engine('sqlite:///bot_memory.db')
Session = sessionmaker(bind=engine)

class Ingatan(Base):
    __tablename__ = 'ingatan'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    role = Column(String)      # user / assistant
    pesan = Column(Text)

Base.metadata.create_all(engine)

# ================== BOT ==================
async def start(update: Update, context):
    await update.message.reply_text("✅ Bot sudah aktif pakai Tencent Hy3 (free)!\nTanya apa saja ya 😊")

async def balas(update: Update, context):
    user_id = update.effective_user.id
    teks = update.message.text

    session = Session()

    # Ambil history lama
    lama = session.query(Ingatan).filter_by(user_id=user_id).all()
    history = [{"role": x.role, "content": x.pesan} for x in lama]
    history.append({"role": "user", "content": teks})

    # Kirim ke Tencent Hy3
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=history[-20:],   # maksimal 20 pesan terakhir
            temperature=0.7,
        )
        jawaban = response.choices[0].message.content
    except Exception as e:
        jawaban = "Maaf, ada error. Coba lagi ya."

    # Simpan ke database permanen
    session.add(Ingatan(user_id=user_id, role="user", pesan=teks))
    session.add(Ingatan(user_id=user_id, role="assistant", pesan=jawaban))
    session.commit()
    session.close()

    await update.message.reply_text(jawaban)

# ================== JALANKAN ==================
if __name__ == "__main__":
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, balas))
    
    print("🤖 Bot Tencent Hy3 sedang berjalan...")
    app.run_polling()
