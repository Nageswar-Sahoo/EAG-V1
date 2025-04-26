# Web Content Search Chrome Extension

A Chrome extension that builds embeddings and FAISS indices for web pages, allowing for semantic search and content highlighting. The extension integrates with a Python Flask API that handles the embedding generation and FAISS indexing.

## Features

- Automatically captures and indexes web page content
- Skips confidential websites (Gmail, WhatsApp, etc.)
- Provides semantic search across your browsing history
- Highlights relevant content when visiting pages
- Shows similarity scores for search results

## Prerequisites

- Python Flask API running on `http://localhost:5000`
- Chrome browser

## Installation

1. Make sure the Python Flask API is running:
```bash
python src/api.py
```

2. Install the Chrome extension:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" in the top right
   - Click "Load unpacked" and select the `chromePlugin` directory

## Usage

1. Click the extension icon in your Chrome toolbar
2. Enter your search query in the search box
3. Click on a result to open the page and highlight the relevant content

## Files

- `manifest.json`: Extension configuration
- `content.js`: Captures page content and handles highlighting
- `popup.html/js`: Search interface
- `background.js`: Handles page processing
- `icons/`: Extension icons (to be added)

## Development

To modify the extension:

1. Make changes to the source files
2. Reload the extension in `chrome://extensions/`
3. Test your changes

## Privacy

- The extension only processes public web pages
- Skips confidential websites (Gmail, WhatsApp, etc.)
- All processing happens through the local Flask API
- No data is sent to external servers 