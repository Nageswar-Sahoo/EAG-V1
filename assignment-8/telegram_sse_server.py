import os
from flask import Flask, Response, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Telegram bot configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Store messages for SSE
message_queue = asyncio.Queue()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming Telegram messages."""
    if str(update.effective_chat.id) == CHAT_ID:
        message = {
            'type': 'message',
            'text': update.message.text,
            'chat_id': update.effective_chat.id
        }
        await message_queue.put(message)
        await update.message.reply_text("Message received and queued for processing!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    await update.message.reply_text("Hello! I'm your SSE-enabled Telegram bot. Send me a message!")

def setup_telegram_bot():
    """Set up the Telegram bot."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Run the bot
    application.run_polling()

@app.route('/events')
def events():
    """SSE endpoint that streams messages from the queue."""
    def generate():
        while True:
            try:
                # Get message from queue (blocking)
                message = asyncio.run(message_queue.get())
                yield f"data: {json.dumps(message)}\n\n"
            except Exception as e:
                print(f"Error in SSE stream: {e}")
                continue

    return Response(generate(), mimetype='text/event-stream')

@app.route('/send_message', methods=['POST'])
async def send_message():
    """Endpoint to send messages back to Telegram."""
    data = request.json
    if not data or 'message' not in data:
        return {'error': 'No message provided'}, 400
    
    try:
        # Create a new application instance for sending messages
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        await application.bot.send_message(chat_id=CHAT_ID, text=data['message'])
        return {'status': 'success'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    # Start the Telegram bot in a separate thread
    import threading
    telegram_thread = threading.Thread(target=setup_telegram_bot)
    telegram_thread.start()
    
    # Start the Flask server
    app.run(host='0.0.0.0', port=5000, debug=True) 