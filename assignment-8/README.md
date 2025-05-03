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

## 📝 Application logs 


  2025-05-03 08:34:07,660 - INFO - [httpx] - HTTP Request: POST https://api.telegram.org/bot7544695746:AAHlffPwULw0HgXrjKxOTAQNY4DLJw3fUzI/getUpdates "HTTP/1.1 200 OK"
2025-05-03 08:34:10,391 - INFO - [httpx] - HTTP Request: POST https://api.telegram.org/bot7544695746:AAHlffPwULw0HgXrjKxOTAQNY4DLJw3fUzI/getUpdates "HTTP/1.1 200 OK"

<h4>2025-05-03 08:34:10,392 - INFO - [__main__] - [2025-05-03 08:34:10] Received message from nageswar in Private Chat (1301883617): Find the Current Point Standings of F1 Racers in 2024 using web search</h4>

2025-05-03 08:34:10,392 - INFO - [__main__] - [2025-05-03 08:34:10] Showing typing indicator...
2025-05-03 08:34:11,015 - INFO - [httpx] - HTTP Request: POST https://api.telegram.org/bot7544695746:AAHlffPwULw0HgXrjKxOTAQNY4DLJw3fUzI/sendChatAction "HTTP/1.1 200 OK"
2025-05-03 08:34:11,015 - INFO - [__main__] - [2025-05-03 08:34:11] Starting message processing...

<h4>2025-05-03 08:34:11,015 - INFO - [__main__] - [2025-05-03 08:34:11] Starting agent processing for message: Find the Current Point Standings of F1 Racers in 2024 using web search</h4>

2025-05-03 08:34:11,016 - INFO - [agent] - Initializing Agent...
2025-05-03 08:34:11,019 - INFO - [__main__] - [2025-05-03 08:34:11] calling agent main function...
2025-05-03 08:34:11,019 - INFO - [agent] - Starting agent...
2025-05-03 08:34:11,019 - INFO - [agent] - Current working directory: /Users/nageswar.sahoo/Desktop/ERAG/EAG-V1/assignment-8
2025-05-03 08:34:11,019 - INFO - [agent] - Connecting to MCP server...
2025-05-03 08:34:11,026 - INFO - [agent] - Connection established, creating session...
2025-05-03 08:34:11,027 - INFO - [agent] - Session created, initializing...
2025-05-03 08:34:12,070 - INFO - [agent] - MCP session initialized
2025-05-03 08:34:12,070 - INFO - [agent] - Requesting tool list...
2025-05-03 08:34:12,070 - INFO - [agent] - Attempt 1 of 3 for function list_tools
2025-05-03 08:34:12,075 - INFO - [agent] - Success on attempt 1
2025-05-03 08:34:12,075 - INFO - [agent] - tool list received...
2025-05-03 08:34:12,075 - INFO - [agent] - 20 tools loaded
2025-05-03 08:34:12,075 - INFO - [agent] - Available tools:
- search_documents: Search for relevant content from uploaded documents.
- add: 
- sqrt: Square root of a number
- subtract: Subtract two numbers
- multiply: Multiply two numbers
- divide: Divide two numbers
- power: Power of two numbers
- cbrt: Cube root of a number
- factorial: factorial of a number
- log: log of a number
- remainder: remainder of two numbers divison
- sin: sin of a number
- cos: cos of a number
- tan: tan of a number
- mine: special mining tool
- create_thumbnail: Create a thumbnail from an image
- strings_to_chars_to_int: Return the ASCII values of the characters in a word
- int_list_to_exponential_sum: Return sum of exponentials of numbers in a list
- fibonacci_numbers: Return the first n Fibonacci Numbers
- search_web: Search the web for real-time content using Tavily API. You can do search for Weather report or any other content.
2025-05-03 08:34:12,075 - INFO - [agent] - Step 1 started
2025-05-03 08:34:12,075 - INFO - [google_genai.models] - AFC is enabled with max remote calls: 10.
2025-05-03 08:34:13,718 - INFO - [httpx] - HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent "HTTP/1.1 200 OK"
2025-05-03 08:34:13,719 - INFO - [google_genai.models] - AFC remote call 1 is done.
2025-05-03 08:34:13,720 - INFO - [agent] - Intent: Find the current standings (point rankings) of Formula 1 racers for the 2024 season., Tool hint: search_documents
2025-05-03 08:34:14,310 - INFO - [agent] - Retrieved 0 relevant memories
2025-05-03 08:34:14,310 - INFO - [google_genai.models] - AFC is enabled with max remote calls: 10.
2025-05-03 08:34:16,376 - INFO - [httpx] - HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent "HTTP/1.1 200 OK"
2025-05-03 08:34:16,379 - INFO - [google_genai.models] - AFC remote call 1 is done.

<h4>2025-05-03 08:34:16,380 - INFO - [agent] - Plan generated: FUNCTION_CALL: search_web|query="F1 2024 current driver standings"</h4>

2025-05-03 08:34:16,380 - INFO - [agent] - Attempt 1 of 3 for function execute_tool
2025-05-03 08:34:20,537 - INFO - [agent] - Success on attempt 1

<h4>2025-05-03 08:34:20,537 - INFO - [agent] - search_web returned: ["Here's what I found:\n\n1. 2024 DRIVER STANDINGS - F1\n   https://www.formula1.com/en/results/driver-standings\n   Pos | Driver | Nationality | Car | Pts\n1 | MaxVerstappenVER | NED | Red Bull Racing Honda RBPT | 437\n2 | LandoNorrisNOR | GBR | McLaren Mercedes | 374\n3 | CharlesLeclercLEC | MON | Ferrari | 356\n4 | O...\n\n2. Formula 1 2024 results and standings for top drivers and teams\n   https://www.motorsport.com/f1/standings/2024/\n   21 | L. LawsonRacing Bulls | 4 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 2 | - | 2 | - | - | -\n22 | V. BottasSauber |  | - | - | - | - | - | - | - | - | - | - | - | - |...\n\n3. 2024 Formula One World Championship - Wikipedia\n   https://en.wikipedia.org/wiki/2024_Formula_One_World_Championship\n   Constructor | No. | Driver | Rounds\nAlpine-Renault | 61 | Jack Doohan | 9, 12\nAston MartinAramco-Mercedes | 34 | Felipe Drugovich | 20, 24\nFerrari | 3839 | Oliver BearmanArthur Leclerc | 2024\nHaas-Fer...\n\n4. 2024 - STATS F1\n   https://www.statsf1.com/en/2024.aspx\n   21. | L. LAWSON |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 2 | - | 2 | - | - | - | 4.00\n22. | V. BOTTAS | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | -...\n\n"]</h4>

2025-05-03 08:34:20,628 - INFO - [agent] - Step 2 started
2025-05-03 08:34:20,628 - INFO - [google_genai.models] - AFC is enabled with max remote calls: 10.
2025-05-03 08:34:23,159 - INFO - [httpx] - HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent "HTTP/1.1 200 OK"
2025-05-03 08:34:23,160 - INFO - [google_genai.models] - AFC remote call 1 is done.
2025-05-03 08:34:23,161 - INFO - [agent] - Intent: The user wants to find the current standings of Formula 1 racers in the 2024 season and has been provided with a few initial search results. The next step depends on whether the provided results fully satisfy the user's request. They probably want to see a full and up-to-date list., Tool hint: check_completeness
2025-05-03 08:34:23,242 - INFO - [agent] - Retrieved 1 relevant memories
2025-05-03 08:34:23,243 - INFO - [google_genai.models] - AFC is enabled with max remote calls: 10.
2025-05-03 08:34:24,847 - INFO - [httpx] - HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent "HTTP/1.1 200 OK"
2025-05-03 08:34:24,848 - INFO - [google_genai.models] - AFC remote call 1 is done.

<h4> 2025-05-03 08:34:24,848 - INFO - [agent] - Plan generated: FINAL_ANSWER: [According to the search results, the top 3 drivers in the 2024 F1 standings are: 1. Max Verstappen (437 points), 2. Lando Norris (374 points), 3. Charles Leclerc (356 points).] </h4>

<h4>2025-05-03 08:34:24,848 - INFO - [agent] - ✅ FINAL RESULT: [According to the search results, the top 3 drivers in the 2024 F1 standings are: 1. Max Verstappen (437 points), 2. Lando Norris (374 points), 3. Charles Leclerc (356 points).]</h4>

<h4>2025-05-03 08:34:24,848 - INFO - [agent] - Connecting to Sheets MCP at http://localhost:8051/sse
<h4>2025-05-03 08:34:24,848 - INFO - [mcp.client.sse] - Connecting to SSE endpoint: http://localhost:8051/sse
2025-05-03 08:34:24,864 - INFO - [httpx] - HTTP Request: POST https://api.telegram.org/bot7544695746:AAHlffPwULw0HgXrjKxOTAQNY4DLJw3fUzI/getUpdates "HTTP/1.1 200 OK"
2025-05-03 08:34:24,869 - INFO - [httpx] - HTTP Request: GET http://localhost:8051/sse "HTTP/1.1 200 OK"
2025-05-03 08:34:24,869 - INFO - [mcp.client.sse] - Received endpoint URL: http://localhost:8051/messages/?session_id=2ef77b9cbcf44e13a213345b2ae66b5c
2025-05-03 08:34:24,869 - INFO - [mcp.client.sse] - Starting post writer with endpoint URL: http://localhost:8051/messages/?session_id=2ef77b9cbcf44e13a213345b2ae66b5c
<h4>2025-05-03 08:34:24,870 - INFO - [agent] - SSE client for Sheets MCP established</h4>
<h4>2025-05-03 08:34:24,870 - INFO - [agent] - ClientSession for Sheets MCP created</h4>
<h4>2025-05-03 08:34:24,872 - INFO - [httpx] - HTTP Request: POST http://localhost:8051/messages/?session_id=2ef77b9cbcf44e13a213345b2ae66b5c "HTTP/1.1 202 Accepted"</h4>
<h4>2025-05-03 08:34:24,873 - INFO - [agent] - Sheets MCP session initialized</h4>
<h4>2025-05-03 08:34:24,873 - INFO - [agent] - Fetching available Sheets tools...</h4>
2025-05-03 08:34:24,875 - INFO - [httpx] - HTTP Request: POST http://localhost:8051/messages/?session_id=2ef77b9cbcf44e13a213345b2ae66b5c "HTTP/1.1 202 Accepted"
2025-05-03 08:34:24,876 - INFO - [httpx] - HTTP Request: POST http://localhost:8051/messages/?session_id=2ef77b9cbcf44e13a213345b2ae66b5c "HTTP/1.1 202 Accepted"
<h4>2025-05-03 08:34:24,878 - INFO - [agent] - Available Sheets tools:</h4>
<h4>2025-05-03 08:34:24,878 - INFO - [agent] -   - process_result: Store result in Google Sheets and return shareable link</h4>
    
    Args:
        result: Dictionary containing the result data to store
    
    Returns:
        Dictionary containing status and spreadsheet link
    

2025-05-03 08:34:24,878 - INFO - [agent] - Storing result in Sheets...
2025-05-03 08:34:24,879 - INFO - [httpx] - HTTP Request: POST http://localhost:8051/messages/?session_id=2ef77b9cbcf44e13a213345b2ae66b5c "HTTP/1.1 202 Accepted"
<h4>2025-05-03 08:34:28,001 - INFO - [agent] - Sheets storage result: meta=None content=[TextContent(type='text', text='{"status": "success", "spreadsheet_link": "https://docs.google.com/spreadsheets/d/17vO7v3hseohWzZgbpmsFY0Y9PQztrDX2lTQl9OmIsNA/edit?usp=drivesdk", "spreadsheet_id": "17vO7v3hseohWzZgbpmsFY0Y9PQztrDX2lTQl9OmIsNA"}', annotations=None)] isError=False
<h4>2025-05-03 08:34:28,001 - INFO - [agent] - Connecting to Email MCP at http://localhost:8052/sse</h4>
<h4>2025-05-03 08:34:28,001 - INFO - [mcp.client.sse] - Connecting to SSE endpoint: http://localhost:8052/sse</h4>
<h4>2025-05-03 08:34:28,022 - INFO - [httpx] - HTTP Request: GET http://localhost:8052/sse "HTTP/1.1 200 OK"</h4>
2025-05-03 08:34:28,023 - INFO - [mcp.client.sse] - Received endpoint URL: http://localhost:8052/messages/?session_id=6abd12e821bf40a18909a9823f7606cd
2025-05-03 08:34:28,023 - INFO - [mcp.client.sse] - Starting post writer with endpoint URL: http://localhost:8052/messages/?session_id=6abd12e821bf40a18909a9823f7606cd</h4>
<h4>2025-05-03 08:34:28,023 - INFO - [agent] - SSE client for Email MCP established</h4>
<h4>2025-05-03 08:34:28,023 - INFO - [agent] - ClientSession for Email MCP created</h4>
<h4>2025-05-03 08:34:28,026 - INFO - [httpx] - HTTP Request: POST http://localhost:8052/messages/?session_id=6abd12e821bf40a18909a9823f7606cd "HTTP/1.1 202 Accepted"</h4>
<h4>2025-05-03 08:34:28,027 - INFO - [agent] - Email MCP session initialized</h4>
<h4>2025-05-03 08:34:28,027 - INFO - [agent] - Fetching available Email tools...</h4>
2025-05-03 08:34:28,028 - INFO - [httpx] - HTTP Request: POST http://localhost:8052/messages/?session_id=6abd12e821bf40a18909a9823f7606cd "HTTP/1.1 202 Accepted"
2025-05-03 08:34:28,029 - INFO - [httpx] - HTTP Request: POST http://localhost:8052/messages/?session_id=6abd12e821bf40a18909a9823f7606cd "HTTP/1.1 202 Accepted"
2025-05-03 08:34:28,031 - INFO - [agent] - Available Email tools:
<h4>2025-05-03 08:34:28,031 - INFO - [agent] -   - send_email: Send email with the Google Sheets result</h4>
    
    Args:
        recipient_email: Email address of the recipient
        subject: Email subject line (optional)
        content: Dictionary containing email content (optional)
    
    Returns:
        Dictionary containing status and message
    
2025-05-03 08:34:28,031 - INFO - [agent] - Preparing email notification...
<h4>2025-05-03 08:34:28,032 - INFO - [httpx] - HTTP Request: POST http://localhost:8052/messages/?session_id=6abd12e821bf40a18909a9823f7606cd "HTTP/1.1 202 Accepted"</h4>
<h4>2025-05-03 08:34:32,185 - INFO - [agent] - Email notification result: meta=None content=[TextContent(type='text', text='{"status": "success", "message": "Email sent successfully to tech.nageswar@gmail.com"}', annotations=None)] isError=False</h4>
<h4>2025-05-03 08:34:32,192 - INFO - [__main__] - [2025-05-03 08:34:32] Agent processing complete. Result: Your result has been stored in Google Sheets and an email notification has been sent.</h4>
2025-05-03 08:34:32,192 - INFO - [__main__] - [2025-05-03 08:34:32] Sending response to user...
2025-05-03 08:34:32,882 - INFO - [httpx] - HTTP Request: POST https://api.telegram.org/bot7544695746:AAHlffPwULw0HgXrjKxOTAQNY4DLJw3fUzI/sendMessage "HTTP/1.1 200 OK"

