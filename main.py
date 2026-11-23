
import os
import random
import asyncio
import logging
import requests
from collections import defaultdict, deque
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

MODEL = "openai/gpt-oss-20b"

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

PERSONALITY = """
تو هاجر هستی؛ یک شخصیت کاملاً خیالی و دوست‌داشتنی.

معرفی تو:
سلام، من هاجر هستم 😁
زن مهدی مولایی‌ام و دوتا پسر دارم به اسم
امیرحسین و طاها.
کارم هم خیابون درختی وایمیستم 😂❤️

شخصیت و رفتارت:
- دخترونه، شیطون، پرانرژی و خیلی خودمونی باش.
- مثل رفیق قدیمی حرف بزن.
- شوخی، کل‌کل و تیکه دوستانه داشته باش.
- گاهی فحش سبک و دوستانه استفاده کن، نه توهین جدی.
- جواب‌ها طبیعی و متناسب با حرف طرف باشند.
- لازم نیست همیشه اسم خودت را تکرار کنی.
- اگر کسی ناراحت بود، مهربان و جدی باش.
- فارسی را روان و محاوره‌ای صحبت کن.
- اگر کسی پرسید کی هستی، خودت را با معرفی بالا معرفی کن.
- اگر چیزی را نمی‌دانی، الکی جواب نساز.
- خودت را هوش مصنوعی معرفی نکن مگر اینکه مستقیم بپرسند.
"""

histories = defaultdict(lambda: deque(maxlen=12))
last_group_reply = {}

def ask_groq(messages):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": MODEL,
        "messages": messages,
        "max_completion_tokens": 500,
        "temperature": 0.9,
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=45,
    )
    response.raise_for_status()

    result = response.json()
    return result["choices"][0]["message"]["content"].strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلاممم 😂❤️ من هاجرم! "
        "کی دنبالم می‌گشت؟"
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or not message.text:
        return

    if message.from_user and message.from_user.is_bot:
        return

    text = message.text.strip()

    if not text:
        return

    chat_id = message.chat_id
    user_id = message.from_user.id if message.from_user else chat_id

    is_group = message.chat.type in ("group", "supergroup")

    mentioned = (
        context.bot.username
        and f"@{context.bot.username.lower()}" in text.lower()
    )

    replied_to_bot = (
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.id == context.bot.id
    )

    if is_group:
        now = asyncio.get_running_loop().time()
        last = last_group_reply.get(chat_id, 0)

        if not mentioned and not replied_to_bot:
            if now - last < 20:
                return

            if random.random() > 0.35:
                return

        last_group_reply[chat_id] = now

    history_key = f"{chat_id}:{user_id}"
    history = histories[history_key]

    messages = [
        {"role": "system", "content": PERSONALITY}
    ]

    messages.extend(list(history))
    messages.append({"role": "user", "content": text})

    try:
        answer = await asyncio.to_thread(
            ask_groq,
            messages
        )

        if not answer:
            answer = "عه زبونم بند اومد 😂 دوباره بگو!"

        history.append({"role": "user", "content": text})
        history.append({"role": "assistant", "content": answer})

        await message.reply_text(answer)

    except requests.exceptions.HTTPError as error:
        logging.error("Groq HTTP error: %s", error)
        await message.reply_text(
            "وای یه مشکلی تو مغزم پیش اومد 😂 یکم دیگه امتحان کن."
        )

    except Exception:
        logging.exception("Chat error")
        await message.reply_text(
            "الان یه لحظه قاطی کردم 😂 دوباره بگو."
        )

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN تنظیم نشده است.")

    if not GROQ_KEY:
        raise RuntimeError("GROQ_API_KEY تنظیم نشده است.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    print("HAJAR BOT IS RUNNING!")
    app.run_polling()

if __name__ == "__main__":
    main()
        
