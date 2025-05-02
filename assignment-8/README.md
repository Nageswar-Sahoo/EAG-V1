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

2025-05-02 20:25:21,691 - INFO - [httpx] - HTTP Request: POST https://api.telegram.org/bot7544695746:AAHlffPwULw0HgXrjKxOTAQNY4DLJw3fUzI/getUpdates "HTTP/1.1 200 OK"

<h4> 2025-05-02 20:25:21,692 - INFO - [__main__] - [2025-05-02 20:25:21] Received message from nageswar in Private Chat (1301883617): Find the Current Point Standings of F1 Racers in 2024 using web search </h4>

2025-05-02 20:25:21,692 - INFO - [__main__] - [2025-05-02 20:25:21] Showing typing indicator...
2025-05-02 20:25:23,310 - INFO - [httpx] - HTTP Request: POST https://api.telegram.org/bot7544695746:AAHlffPwULw0HgXrjKxOTAQNY4DLJw3fUzI/sendChatAction "HTTP/1.1 200 OK"
2025-05-02 20:25:23,312 - INFO - [__main__] - [2025-05-02 20:25:23] Starting message processing...
2025-05-02 20:25:23,312 - INFO - [__main__] - [2025-05-02 20:25:23] Starting agent processing for message: Find the Current Point Standings of F1 Racers in 2024 using web search
2025-05-02 20:25:23,312 - INFO - [agent] - [2025-05-02 20:25:23] Initializing Agent...
2025-05-02 20:25:23,315 - INFO - [agent] - [2025-05-02 20:25:23] Agent initialized with empty tool list
2025-05-02 20:25:23,315 - INFO - [__main__] - [2025-05-02 20:25:23] calling agent main function...
2025-05-02 20:25:23,315 - INFO - [agent] - [2025-05-02 20:25:23] Starting agent...
2025-05-02 20:25:23,316 - INFO - [agent] - [2025-05-02 20:25:23] Current working directory: /Users/nageswar.sahoo/Desktop/ERAG/EAG-V1/assignment-8
2025-05-02 20:25:23,316 - INFO - [agent] - [2025-05-02 20:25:23] Connecting to MCP server...
2025-05-02 20:25:23,324 - INFO - [agent] - [2025-05-02 20:25:23] Connection established, creating session...
2025-05-02 20:25:23,324 - INFO - [agent] - [2025-05-02 20:25:23] Session created, initializing...
2025-05-02 20:25:24,436 - INFO - [agent] - [2025-05-02 20:25:24] MCP session initialized
2025-05-02 20:25:24,436 - INFO - [agent] - [2025-05-02 20:25:24] Requesting tool list...
2025-05-02 20:25:24,441 - INFO - [agent] - [2025-05-02 20:25:24] tool list received...
2025-05-02 20:25:24,441 - INFO - [agent] - [2025-05-02 20:25:24] 20 tools loaded
2025-05-02 20:25:24,441 - INFO - [agent] - [2025-05-02 20:25:24] Available tools:
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
2025-05-02 20:25:24,442 - INFO - [agent] - [2025-05-02 20:25:24] Step 1 started
2025-05-02 20:25:24,442 - INFO - [google_genai.models] - AFC is enabled with max remote calls: 10.
2025-05-02 20:25:27,185 - INFO - [httpx] - HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent "HTTP/1.1 200 OK"
2025-05-02 20:25:27,185 - INFO - [google_genai.models] - AFC remote call 1 is done.
  
<h4> 2025-05-02 20:25:27,186 - INFO - [agent] - [2025-05-02 20:25:27] Intent: Find the current Formula 1 (F1) racer standings for the 2024 season., Tool hint: search_web </h4>

2025-05-02 20:25:27,772 - INFO - [agent] - [2025-05-02 20:25:27] Retrieved 0 relevant memories
2025-05-02 20:25:27,772 - INFO - [google_genai.models] - AFC is enabled with max remote calls: 10.
2025-05-02 20:25:29,974 - INFO - [httpx] - HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent "HTTP/1.1 200 OK"
2025-05-02 20:25:29,975 - INFO - [google_genai.models] - AFC remote call 1 is done.

<h4> 2025-05-02 20:25:29,975 - INFO - [agent] - [2025-05-02 20:25:29] Plan generated: FUNCTION_CALL: search_web|query="F1 racer standings 2024" </h4>

2025-05-02 20:25:32,972 - INFO - [httpx] - HTTP Request: POST https://api.telegram.org/bot7544695746:AAHlffPwULw0HgXrjKxOTAQNY4DLJw3fUzI/getUpdates "HTTP/1.1 200 OK"

<h4>  2025-05-02 20:25:34,238 - INFO - [agent] - [2025-05-02 20:25:34] search_web returned: ["Here's what I found:\n\n1. 2024 F1 Driver Standings - GPFans\n   https://www.gpfans.com/en/f1-standings/2024/\n   2024 F1 Driver Standings\nF1 Drivers F1 Constructors\nSeason  \n| Pos | Driver | Team | PTS. |\n| --- | --- | --- | --- |\n| 01 | \nMax VERSTAPPEN\n| Red Bull Racing | 437 |\n| 02 | \nLando NORRIS\n| McLaren | ...\n\n2. Formula 1 2024 results and standings for top drivers and teams\n   https://www.motorsport.com/f1/standings/2024/\n   | 1 |   M. Verstappen Red Bull Racing | 437 | 26/1 | 25/1 | - | 26/1 | 33 | 26 | 25/1 | 8/6 | 25/1 | 25/1 | 18 | 18/2 | 10/5 | 12/4 | 18/2 | 8/6 | 10/5 | 18/2 | 23 | 8/6 | 31 | 10/5 | 26 | 8/6 |\n| 2 |...\n\n3. 2024 - STATS F1\n   https://www.statsf1.com/en/2024.aspx\n   21. | L. LAWSON |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 2 | - | 2 | - | - | - | 4.00\n22. | V. BOTTAS | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | -...\n\n4. 2024 F1 standings | GRR - Goodwood\n   https://www.goodwood.com/grr/f1/2024-f1-standings/\n   2024 F1 drivers' standings ; 3. Charles Leclerc. Ferrari ; 4. Oscar Piastri. McLaren ; 5. Carlos Sainz Jr. Ferrari ; 6. George Russell. Mercedes-AMG....\n\n5. 2024 Formula One World Championship - Wikipedia\n   https://en.wikipedia.org/wiki/2024_Formula_One_World_Championship\n   F1 TeamHaas-FerrariVF-24[13]Ferrari 066/10[14][15]205027\xa0Kevin Magnussen\xa0Oliver Bearman\xa0Nico Hülkenberg1–16, 18–24[b]17, 21All\xa0McLaren Formula 1 TeamMcLaren-MercedesMCL38[17]Mercedes-AMG F1 M15[7][18]...\n\n"] <h4> 
   
2025-05-02 20:25:34,340 - INFO - [agent] - [2025-05-02 20:25:34] Step 2 started
2025-05-02 20:25:34,340 - INFO - [google_genai.models] - AFC is enabled with max remote calls: 10.
2025-05-02 20:25:36,929 - INFO - [httpx] - HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent "HTTP/1.1 200 OK"
2025-05-02 20:25:36,932 - INFO - [google_genai.models] - AFC remote call 1 is done.
2025-05-02 20:25:36,932 - INFO - [agent] - [2025-05-02 20:25:36] Intent: The user is trying to find the current point standings for F1 racers in the 2024 season using web search and has already performed an initial search., Tool hint: search_documents
2025-05-02 20:25:37,025 - INFO - [agent] - [2025-05-02 20:25:37] Retrieved 1 relevant memories
2025-05-02 20:25:37,026 - INFO - [google_genai.models] - AFC is enabled with max remote calls: 10.
2025-05-02 20:25:39,662 - INFO - [httpx] - HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent "HTTP/1.1 200 OK"
2025-05-02 20:25:39,663 - INFO - [google_genai.models] - AFC remote call 1 is done.

<h4>  2025-05-02 20:25:39,663 - INFO - [agent] - [2025-05-02 20:25:39] Plan generated: FINAL_ANSWER: [According to the search results, Max Verstappen (Red Bull Racing) is currently leading the 2024 F1 Driver Standings with 437 points. Lando Norris (McLaren) is also mentioned, and further standings information for other drivers like Charles Leclerc, Oscar Piastri, Carlos Sainz Jr., and George Russell can be found in the provided links.] <h4> 

<h4> 2025-05-02 20:25:39,663 - INFO - [agent] - [2025-05-02 20:25:39] ✅ FINAL RESULT: [According to the search results, Max Verstappen (Red Bull Racing) is currently leading the 2024 F1 Driver Standings with 437 points. Lando Norris (McLaren) is also mentioned, and further standings information for other drivers like Charles Leclerc, Oscar Piastri, Carlos Sainz Jr., and George Russell can be found in the provided links.] </h4>
2025-05-02 20:25:43,134 - INFO - [httpx] - HTTP Request: POST https://api.telegram.org/bot7544695746:AAHlffPwULw0HgXrjKxOTAQNY4DLJw3fUzI/getUpdates "HTTP/1.1 200 OK"

<h4> 2025-05-02 20:25:48,525 - INFO - [__main__] - [2025-05-02 20:25:48] Agent processing complete. Result: Your result has been stored in Google Sheets and an email notification has been sent. </h4>

2025-05-02 20:25:48,525 - INFO - [__main__] - [2025-05-02 20:25:48] Sending response to user...
2025-05-02 20:25:49,238 - INFO - [httpx] - HTTP Request: POST https://api.telegram.org/bot7544695746:AAHlffPwULw0HgXrjKxOTAQNY4DLJw3fUzI/sendMessage "HTTP/1.1 200 OK"

