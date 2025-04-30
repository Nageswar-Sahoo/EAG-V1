# Web Content Search Extension

A Chrome extension that builds embeddings and FAISS indices for web pages, with search functionality and content highlighting.

## Features

- Automatically processes web pages and builds embeddings
- Stores content in a FAISS index for efficient similarity search
- Provides a popup interface for searching across indexed content
- Highlights matching content when opening search results
- Skips confidential websites (Gmail, WhatsApp, etc.)

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with:
```
GEMINI_API_KEY=your_api_key_here
```

3. Load the Chrome extension:
- Open Chrome and go to `chrome://extensions/`
- Enable "Developer mode"
- Click "Load unpacked" and select the `chromePlugin` directory

4. Start the backend server:
```bash
python src/api.py
```

## Usage

1. Browse the web normally - the extension will automatically process pages
2. Click the extension icon to open the search popup
3. Enter your search query
4. Click on a result to open the page with the matching content highlighted

## Architecture

The system consists of several components:

- `agent.py`: Main agent coordinating the system
- `perception.py`: Extracts structured information from user input
- `memory.py`: Manages FAISS index and memory storage
- `decision.py`: Generates plans using LLM
- `action.py`: Executes tool calls

The Chrome extension includes:
- `manifest.json`: Extension configuration
- `content.js`: Processes web pages
- `background.js`: Handles tab updates
- `popup.html/js`: Search interface

## Notes

- The extension skips confidential websites like Gmail, WhatsApp, etc.
- Content is processed in chunks for better embedding quality
- The FAISS index is stored locally for persistence
- Search results include similarity scores and direct links to content
