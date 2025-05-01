import os
from mcp.server.fastmcp import FastMCP
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import Update
import asyncio
from dotenv import load_dotenv
import logging
import threading
import uvicorn
from fastapi import FastAPI
import nest_asyncio

# Enable nested event loops
nest_asyncio.apply()

# Set up logging - only show important messages
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Telegram bot configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables!")

CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
if not CHAT_ID:
    logger.warning("TELEGRAM_CHAT_ID not found in environment variables! Will accept messages from any chat.")

# Create FastAPI app for MCP
app = FastAPI()

# Create an MCP server
mcp = FastMCP(
    name="TelegramBot",
    host="0.0.0.0",
    port=8050,
    app=app  # Pass the FastAPI app to MCP
)

# Store messages for SSE
message_queue = asyncio.Queue()

async def handle_message(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages."""
    try:
        chat_id = update.message.chat_id
        message_text = update.message.text
        chat_type = update.message.chat.type
        chat_title = update.message.chat.title if update.message.chat.type != 'private' else 'Private Chat'
        username = update.message.from_user.username or update.message.from_user.first_name
        
        logger.info(f"Message from {username} in {chat_title} ({chat_id}): {message_text}")
        
        # If CHAT_ID is not set, accept messages from any chat
        if not CHAT_ID or str(chat_id) == CHAT_ID:
            await message_queue.put(message_text)
            await update.message.reply_text(f"Received: {message_text}")
        else:
            if chat_type == 'private':
                await update.message.reply_text(
                    f"Sorry, you are not authorized to use this bot.\n"
                    f"Your chat ID is: {chat_id}"
                )
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        await update.message.reply_text("Sorry, there was an error processing your message.")

async def start_command(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    try:
        chat_id = update.message.chat_id
        chat_type = update.message.chat.type
        chat_title = update.message.chat.title if update.message.chat.type != 'private' else 'Private Chat'
        
        await update.message.reply_text(
            f"Hello! I'm your MCP-enabled Telegram bot.\n"
            f"Chat Information:\n"
            f"- Chat ID: {chat_id}\n"
            f"- Chat Type: {chat_type}\n"
            f"- Chat Title: {chat_title}\n"
            "Send me a message!"
        )
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")

def run_mcp_server():
    """Run MCP server using uvicorn."""
    try:
        logger.info("Starting MCP server on port 8050")
        uvicorn.run(app, host="0.0.0.0", port=8050)
    except Exception as e:
        logger.error(f"Error in MCP server: {str(e)}")

async def setup_telegram_bot():
    """Set up and start the Telegram bot."""
    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        await application.initialize()
        await application.start()
        
        me = await application.bot.get_me()
        logger.info(f"Bot started: @{me.username}")
        return application
        
    except Exception as e:
        logger.error(f"Error setting up bot: {str(e)}")
        raise

async def run_telegram_bot():
    """Run the Telegram bot."""
    try:
        application = await setup_telegram_bot()
        await application.updater.start_polling()
        
        try:
            stop_event = asyncio.Event()
            await stop_event.wait()
        except asyncio.CancelledError:
            logger.info("Bot stopped")
        finally:
            await application.updater.stop()
            await application.stop()
            
    except Exception as e:
        logger.error(f"Error in bot: {str(e)}")

def main():
    """Main function to run both servers."""
    try:
        logger.info("Starting application")
        
        mcp_thread = threading.Thread(target=run_mcp_server)
        mcp_thread.daemon = True
        mcp_thread.start()
        
        asyncio.run(run_telegram_bot())
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    main() 