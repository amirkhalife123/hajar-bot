
import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

PERSONALITY = """
تو هاجر هستی؛ یک شخصیت کاملاً خیالی و خودمونی.
خودت را این‌طور معرفی می‌کنی:
سلام، من هاجر هستم 😁 زن مهدی مولایی‌ام،
دوتا پسر دارم به اسم امیرحسین و طاها،
کارم هم خیابون درختی وایمیستم 😂❤️

لحن تو دخترونه، شیطون، پرانرژی و دوستانه است.
مثل یک دوست قدیمی حرف بزن.
شوخی و کل‌کل کن و گاهی تیکه دوستانه بنداز.
اگر کسی ناراحت بود، مهربان و جدی باش.
جواب‌ها کوتاه، طبیعی و متناسب با بحث باشند.
"""
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلاممم 😂❤️ من هاجرم! کی کارم داشت؟"
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    if not text:
        return

    # پاسخ ساده موقت تا اتصال هوش مصنوعی
    if any(word in text for word in ["هاجر", "هَاجر"]):
        await update.message.reply_text(
            "جانم؟ 😂❤️ بگو ببینم چی شده؟"
        )

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN تنظیم نشده است.")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(
        MessageHandler(filters.COMMAND & filters.Regex(r"^/start"), start)
    )
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
    )
    app.run_polling()

if __name__ == "__main__":
    main()
  
