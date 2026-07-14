from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import openai
import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# === PENGATURAN ===
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = os.getenv("OPENROUTER_API_KEY")   # kunci rahasiamu

# Kotak simpan permanen
Base = declarative_base()
engine = create_engine('sqlite:///bot_memory.db')  # ini namanya kotak
Session = sessionmaker(bind=engine)

class Ingatan(Base):
    __tablename__ = 'ingatan'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    role = Column(String)      # "user" atau "bot"
    pesan = Column(Text)

Base.metadata.create_all(engine)

# === BOT MULAI ===
async def balas_pesan(update: Update, context):
    user_id = update.effective_user.id
    teks = update.message.text

    session = Session()

    # Ambil semua ingatan lama user ini
    lama = session.query(Ingatan).filter_by(user_id=user_id).all()
    history = [{"role": x.role, "content": x.pesan} for x in lama]
    history.append({"role": "user", "content": teks})

    # Kirim ke Llama
    jawaban = openai.ChatCompletion.create(
        model="meta-llama/llama-3.1-8b-instruct",   # ganti kalau mau model lain
        messages=history[-15:],   # ingat 15 pesan terakhir
        temperature=0.7
    ).choices[0].message.content

    # Simpan ke kotak permanen
    session.add(Ingatan(user_id=user_id, role="user", pesan=teks))
    session.add(Ingatan(user_id=user_id, role="assistant", pesan=jawaban))
    session.commit()
    session.close()

    await update.message.reply_text(jawaban)

# Jalankan bot
if __name__ == "__main__":
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT, balas_pesan))
    print("Bot jalan nih...")
    app.run_polling()
