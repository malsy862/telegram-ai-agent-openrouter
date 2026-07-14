import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from openai import OpenAI
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = "llama3-70b-8192"   # <-- Model ini yang aktif

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

async def start(update: Update, context):
    await update.message.reply_text("✅ Bot Groq aktif dengan Llama3 70B!\nTanya apa saja.")

async def balas(update: Update, context):
    user_id = update.effective_user.id
    teks = update.message.text

    await update.message.reply_text("⏳ Sedang berpikir...")

    session = Session()
    lama = session.query(Ingatan).filter_by(user_id=user_id).all()
    history = [{"role": x.role, "content": x.pesan} for x in lama]
    history.append({"role": "user", "content": teks})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=history[-12:],
            temperature=0.7,
            max_tokens=700,
        )
        jawaban = response.choices[0].message.content
    except Exception as e:
        print(f"Error: {str(e)}")
        jawaban = "Maaf, ada masalah. Coba lagi ya."

    session.add(Ingatan(user_id=user_id, role="user", pesan=teks))
    session.add(Ingatan(user_id=user_id, role="assistant", pesan=jawaban))
    session.commit()
    session.close()

    await update.message.reply_text(jawaban)

if __name__ == "__main__":
    TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")
    print("Bot mulai...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, balas))
    app.run_polling()
