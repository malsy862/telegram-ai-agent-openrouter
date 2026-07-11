# Telegram AI Agent - OpenRouter

🤖 **Telegram Bot AI Agent** yang powerful menggunakan **OpenRouter**.

Bisa pakai model Claude, Grok, Llama, Gemini, dll.

## Fitur
- Percakapan natural dengan **memory** (ingat riwayat chat)
- Mudah di-deploy ke **Railway**
- Support perintah `/start` dan `/clear`
- System prompt dalam Bahasa Indonesia

## Tech Stack
- Python 3
- python-telegram-bot v22
- OpenAI SDK (kompatibel OpenRouter)

## Cara Deploy
1. Deploy repo ini ke [Railway.app](https://railway.app)
2. Tambahkan Environment Variables:
   - `TELEGRAM_BOT_TOKEN` → dari @BotFather
   - `OPENROUTER_API_KEY` → dari openrouter.ai
3. Set **Start Command**: `python main.py`

Bot siap digunakan!

---
Made with ❤️ untuk komunitas AI Indonesia
