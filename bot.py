import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

import os

# 从环境变量读取配置，方便在 Zeabur 上改
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHAT_ID = int(os.getenv("SOURCE_CHAT_ID", "0"))
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID", "0"))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # 只处理来自源群的消息
    if chat_id != SOURCE_CHAT_ID:
        return

    message = update.effective_message

    try:
        # 用 copy_message，看起来像新发的，不带“转发自”的标记
        await context.bot.copy_message(
            chat_id=TARGET_CHAT_ID,
            from_chat_id=chat_id,
            message_id=message.id,
        )
    except Exception as e:
        logger.error(f"Failed to forward message: {e}")


async def on_startup(app):
    logger.info("Bot started and is now listening for messages...")


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.ALL, forward_message))

    app.post_init = on_startup

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
