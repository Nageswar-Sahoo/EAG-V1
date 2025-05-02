# AI Assistant with Telegram, Google Sheets, and Email Integration

This project implements an intelligent AI assistant that can process user queries through Telegram, store results in Google Sheets, and send email notifications. It uses a multi-server architecture with MCP (Message Control Protocol) servers to handle different functionalities.

## 🌟 Features

- **Telegram Bot Integration**: Process user queries in real-time through a Telegram bot
- **Google Sheets Integration**: Automatically store results in Google Sheets for easy access and sharing
- **Email Notifications**: Send formatted HTML emails with query results and spreadsheet links
- **Intelligent Processing**: Uses advanced NLP to understand and process user queries
- **Memory Management**: Maintains context and history of conversations
- **Error Handling**: Robust error handling with retries and graceful degradation
- **Logging**: Comprehensive logging system for debugging and monitoring

## 🛠️ Technology Stack

- Python 3.8+
- FastAPI
- Google Sheets API
- Gmail SMTP
- Telegram Bot API
- Async/Await Architecture
- MCP (Message Control Protocol)

## 📋 Prerequisites

Before running the application, you need:

1. Python 3.8 or higher
2. A Google Cloud Project with:
   - Google Sheets API enabled
   - Google Drive API enabled
   - OAuth 2.0 credentials
3. A Gmail account with:
   - 2-Step Verification enabled
   - App Password generated
4. A Telegram Bot Token

## 🚀 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Install dependencies:
```bash
uv  pip install . (all dependecy is under pyproject.toml)
```

3. Set up environment variables in `.env`:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
GMAIL_ADDRESS=your_gmail_address
GMAIL_APP_PASSWORD=your_gmail_app_password
```

4. Place your Google OAuth credentials in the project directory:
```bash
mv /path/to/downloaded/credentials.json .
```

## 🏃‍♂️ Running the Application

1. Start the Sheets MCP Server:
```bash
python src/sheets_mcp_server.py
```

2. Start the Email MCP Server:
```bash
python src/email_mcp_server.py
```

3. Start the Telegram Bot:
```bash
python src/telegram_mcp_server.py
```

## 🔧 Configuration

### Google Sheets Setup
1. Go to Google Cloud Console
2. Create a new project
3. Enable Google Sheets and Drive APIs
4. Create OAuth 2.0 credentials
5. Configure the OAuth consent screen
6. Add your email as a test user

### Gmail Setup
1. Enable 2-Step Verification
2. Generate App Password
3. Use the generated password in .env file

### Telegram Bot Setup
1. Create a new bot with BotFather
2. Get the bot token
3. Add token to .env file
4. Start a chat with your bot
5. Get your chat ID

## 📁 Project Structure

```
.
├── src/
│   ├── agent.py              # Main agent logic
│   ├── sheets_mcp_server.py  # Google Sheets integration
│   ├── email_mcp_server.py   # Email notification service
│   ├── telegram_mcp_server.py# Telegram bot server
│   ├── perception.py         # Query understanding
│   ├── memory.py            # Memory management
│   ├── decision.py          # Decision making
│   └── action.py            # Action execution
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
├── credentials.json         # Google OAuth credentials
└── README.md               # This file
```

## 🔄 Workflow

1. User sends a query through Telegram
2. Agent processes the query using:
   - Perception (understanding)
   - Memory (context)
   - Decision (planning)
   - Action (execution)
3. Results are stored in Google Sheets
4. Email notification is sent with results
5. Response is sent back to Telegram

## 🛡️ Error Handling

- Retry mechanism with exponential backoff
- Graceful degradation when services are unavailable
- Comprehensive error logging
- User-friendly error messages

## 📝 Logging

Logs are stored in:
- `agent.log`
- `sheets_mcp_server.log`
- `email_mcp_server.log`
- `telegram_bot.log`
