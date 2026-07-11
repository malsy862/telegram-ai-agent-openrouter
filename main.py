import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-70b-instruct")

if not BOT_TOKEN or not OPENROUTER_API_KEY:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN dan OPENROUTER_API_KEY harus diisi di environment variable!")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

conversation_history = {}

SYSTEM_PROMPT = """Kamu adalah AI Agent Telegram yang ramah, cerdas, dan membantu.
Jawab dalam bahasa yang sama dengan user (biasanya Bahasa Indonesia).
Jaga percakapan tetap natural dan engaging."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    conversation_history[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    await update.message.reply_text(
        "👋 Halo! Saya **AI Agent** powered by OpenRouter.\n"
        "Kirim pesan apa saja, saya akan jawab.\n\n"
        "Perintah:\n"
        "/clear - Hapus riwayat percakapan"
    )

async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in conversation_history:
        conversation_history[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    await update.message.reply_text("✅ Riwayat percakapan sudah dibersihkan!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_message = update.message.text

    if chat_id not in conversation_history:
        conversation_history[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    conversation_history[chat_id].append({"role": "user", "content": user_message})

    if len(conversation_history[chat_id]) > 12:
        conversation_history[chat_id] = [conversation_history[chat_id][0]] + conversation_history[chat_id][-10:]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=conversation_history[chat_id],
            max_tokens=1500,
            temperature=0.7,
            extra_headers={
                "HTTP-Referer": "https://github.com/username/telegram-ai-agent",
                "X-Title": "Telegram AI Agent - OpenRouter",
            },
        )

        ai_response = response.choices[0].message.content.strip()
        conversation_history[chat_id].append({"role": "assistant", "content": ai_response})
        await update.message.reply_text(ai_response)

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Maaf, terjadi kesalahan. Coba lagi dalam beberapa saat.")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear_history))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("🤖 Bot berjalan dengan polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
