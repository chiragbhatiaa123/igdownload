
import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from telegram.error import BadRequest
from instagram import InstagramDownloader

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize Downloader
downloader = InstagramDownloader(download_path="downloads")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Instagram Downloader Bot!\n\n"
        "Send me an Instagram link (Post, Reel, or Carousel) and I'll download it for you."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Just send a link like:\n"
        "https://www.instagram.com/p/CoMpLeXc0dE/\n\n"
        "I support Posts, Reels, and Carousels."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "instagram.com" not in url:
        await update.message.reply_text("Please send a valid Instagram link.")
        return

    status_msg = await update.message.reply_text("Downloading... ⏳")

    try:
        # Run synchronous download in a separate thread to not block the bot
        loop = asyncio.get_event_loop()
        files, post_type, folder_path = await loop.run_in_executor(None, downloader.download_post, url)
        
        await context.bot.edit_message_text("Uploading... 🚀", chat_id=update.effective_chat.id, message_id=status_msg.message_id)

        chat_id = update.effective_chat.id
        
        # Decide how to send based on file count or type
        if len(files) == 1:
            file_path = files[0]
            if file_path.endswith('.mp4'):
                await context.bot.send_video(chat_id=chat_id, video=open(file_path, 'rb'))
            else:
                await context.bot.send_photo(chat_id=chat_id, photo=open(file_path, 'rb'))
        else:
            # Carousel / Multiple files
            media_group = []
            for f in files:
                if f.endswith('.mp4'):
                    media_group.append(InputMediaVideo(media=open(f, 'rb')))
                else:
                    media_group.append(InputMediaPhoto(media=open(f, 'rb')))
            
            # Telegram limits media groups to 10 items. We might need to chunk if > 10.
            # Instaloader downloads all parts.
            
            chunk_size = 10
            for i in range(0, len(media_group), chunk_size):
                chunk = media_group[i:i + chunk_size]
                try:
                    await context.bot.send_media_group(chat_id=chat_id, media=chunk)
                except BadRequest as e:
                    logger.error(f"Error sending media group chunk: {e}")
                    await update.message.reply_text(f"Error uploading some files: {e}")

        # Cleanup
        await context.bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
        downloader.cleanup(folder_path)

    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        error_text = str(e)
        if "Login required" in error_text:
             error_text = "This post requires login/ is private."
             
        await context.bot.edit_message_text(f"❌ Error: {error_text}", chat_id=update.effective_chat.id, message_id=status_msg.message_id)
        # Try to cleanup if path was created but not returned (handled in downloader mostly)

if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env")
        exit(1)

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # Generic error handler
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error(msg="Exception while handling an update:", exc_info=context.error)

    application.add_error_handler(error_handler)

    print("Bot is running...")
    application.run_polling()
