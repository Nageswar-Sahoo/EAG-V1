import os
from mcp.server.fastmcp import FastMCP
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio
from dotenv import load_dotenv
import logging
import threading
import nest_asyncio
from agent import Agent
import datetime

# Enable nested event loops
nest_asyncio.apply()

# Set up logging with more detailed format
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('telegram_bot.log')
    ]
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


# Create an MCP server
mcp = FastMCP(
    name="TelegramBot",
    host="0.0.0.0",
    port=8050,
)

# Store messages for SSE
message_queue = asyncio.Queue()

def log_with_timestamp(message: str, level: str = "INFO"):
    """Helper function to log messages with timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    logger.info(log_message)

    # if level == "INFO":
    #     logger.info(log_message)
    # elif level == "DEBUG":
    #     logger.debug(log_message)
    # elif level == "WARNING":
    #     logger.warning(log_message)
    # elif level == "ERROR":
    #     logger.error(log_message)

async def process_with_agent(message: str) -> str:
    """Process message using the Agent class."""
    try:
        log_with_timestamp(f"Starting agent processing for message: {message}")

        agent = Agent()
        log_with_timestamp("calling agent main function...")

        result = await agent.main(message)
        log_with_timestamp(f"Agent processing complete. Result: {result[:100]}...")
        return result
                
    except Exception as e:
        log_with_timestamp(f"Error in agent processing: {str(e)}", "ERROR")
        return f"Sorry, I encountered an error while processing your request: {str(e)}"

async def handle_message(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages."""
    try:
        chat_id = update.message.chat_id
        message_text = update.message.text
        chat_type = update.message.chat.type
        chat_title = update.message.chat.title if update.message.chat.type != 'private' else 'Private Chat'
        username = update.message.from_user.username or update.message.from_user.first_name
        
        log_with_timestamp(f"Received message from {username} in {chat_title} ({chat_id}): {message_text}")
        
        # If CHAT_ID is not set, accept messages from any chat
        if not CHAT_ID or str(chat_id) == CHAT_ID:
            # Show typing indicator
            log_with_timestamp("Showing typing indicator...")
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
            
            # Process message with agent
            log_with_timestamp("Starting message processing...")
            response = await process_with_agent(message_text)
            
            # Send response back to user
            log_with_timestamp("Sending response to user...")
            await update.message.reply_text(response)
            
            # Store in message queue for SSE
            log_with_timestamp("Storing message in queue...")
            await message_queue.put(message_text)
        else:
            log_with_timestamp(f"Unauthorized access attempt from chat {chat_id}", "WARNING")
            if chat_type == 'private':
                await update.message.reply_text(
                    f"Sorry, you are not authorized to use this bot.\n"
                    f"Your chat ID is: {chat_id}"
                )
    except Exception as e:
        log_with_timestamp(f"Error processing message: {str(e)}", "ERROR")
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
        mcp.run(transport="sse")
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