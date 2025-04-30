from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from pathlib import Path
import faiss
import numpy as np
import requests
from dotenv import load_dotenv
import json
import time
from markitdown import MarkItDown
from tqdm import tqdm
import hashlib
from agent import Agent, log
from perception import extract_perception
from memory import MemoryManager, MemoryItem
from decision import generate_plan
from action import execute_tool, parse_function_call

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()
ROOT = Path(__file__).parent.resolve()

# Configuration
EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 40

# Create necessary directories
FAISS_DIR = ROOT / "faiss_index"
FAISS_DIR.mkdir(exist_ok=True)
FAISS_INDEX_PATH = FAISS_DIR / "index.bin"
METADATA_PATH = FAISS_DIR / "metadata.json"
CACHE_FILE = FAISS_DIR / "doc_index_cache.json"

# Initialize FAISS index and metadata
index = None
metadata = []

# Initialize agent and memory manager
agent = Agent()
memory_manager = MemoryManager()

def load_faiss_index():
    global index, metadata
    try:
        if FAISS_INDEX_PATH.exists():
            index = faiss.read_index(str(FAISS_INDEX_PATH))
        if METADATA_PATH.exists():
            with open(METADATA_PATH, 'r') as f:
                metadata = json.load(f)
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        index = None
        metadata = []

def get_embedding(text: str) -> np.ndarray:
    response = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "prompt": text})
    response.raise_for_status()
    return np.array(response.json()["embedding"], dtype=np.float32)

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    for i in range(0, len(words), size - overlap):
        yield " ".join(words[i:i+size])

def file_hash(path):
    return hashlib.md5(Path(path).read_bytes()).hexdigest()

def ensure_faiss_ready():
    global index, metadata
    if index is None:
        process_documents()

def process_documents():
    global index, metadata
    load_faiss_index()
    
    CACHE_META = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}
    converter = MarkItDown()
    
    # Process new documents
    for file in Path(ROOT/"documents").glob("*.*"):
        fhash = file_hash(file)
        if file.name in CACHE_META and CACHE_META[file.name] == fhash:
            continue
        
        try:
            result = converter.convert(str(file))
            markdown = result.text_content
            chunks = list(chunk_text(markdown))
            embeddings_for_file = []
            new_metadata = []
            
            for i, chunk in enumerate(tqdm(chunks, desc=f"Embedding {file.name}")):
                embedding = get_embedding(chunk)
                embeddings_for_file.append(embedding)
                new_metadata.append({
                    "doc": file.name,
                    "chunk": chunk,
                    "chunk_id": f"{file.stem}_{i}"
                })
            
            if embeddings_for_file:
                if index is None:
                    dim = len(embeddings_for_file[0])
                    index = faiss.IndexFlatL2(dim)
                index.add(np.stack(embeddings_for_file))
                metadata.extend(new_metadata)
            
            CACHE_META[file.name] = fhash
            
        except Exception as e:
            print(f"Failed to process {file.name}: {e}")
    
    # Save updated index and metadata
    if index and index.ntotal > 0:
        faiss.write_index(index, str(FAISS_INDEX_PATH))
        with open(METADATA_PATH, 'w') as f:
            json.dump(metadata, f, indent=2)
        with open(CACHE_FILE, 'w') as f:
            json.dump(CACHE_META, f, indent=2)

def is_confidential_url(url: str) -> bool:
    confidential_domains = [
        'mail.google.com',
        'web.whatsapp.com',
        'facebook.com',
        'messenger.com',
        'linkedin.com',
        'twitter.com'
    ]
    return any(domain in url for domain in confidential_domains)

@app.route('/process_page', methods=['POST'])
def process_page():
    data = request.json
    url = data.get('url')
    content = data.get('content')
    
    if not url or not content:
        return jsonify({'error': 'Missing url or content'}), 400
    
    if is_confidential_url(url):
        return jsonify({'error': 'Confidential URL skipped'}), 403
    
    try:
        ensure_faiss_ready()
        
        # Process content in chunks
        chunks = list(chunk_text(content))
        embeddings = []
        new_metadata = []
        
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            embeddings.append(embedding)
            new_metadata.append({
                'url': url,
                'chunk': chunk,
                'chunk_id': f"{hashlib.md5(url.encode()).hexdigest()}_{i}",
                'timestamp': time.time()
            })
        
        # Add to FAISS index
        if embeddings:
            index.add(np.stack(embeddings))
            metadata.extend(new_metadata)
            
            # Save updated index and metadata
            faiss.write_index(index, str(FAISS_INDEX_PATH))
            with open(METADATA_PATH, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    
    if not query:
        log("search", "Error: Missing query parameter")
        return jsonify({'error': 'Missing query'}), 400
    
    try:
        log("search", f"Processing search query: {query}")
        
        # Use agent system to process the query
        log("search", "Extracting perception from query")
        perception = extract_perception(query)
        log("search", f"Perception extracted: {perception.model_dump()}")
        
        # Get relevant memories
        log("search", "Retrieving relevant memories")
        memory_items = memory_manager.retrieve(query, top_k=3)
        log("search", f"Retrieved {len(memory_items)} relevant memories")
        
        # Generate plan using the agent system
        log("search", "Generating plan using agent system")
        plan = generate_plan(
            perception=perception,
            memory_items=memory_items,
            tool_descriptions="Use search_documents tool to find relevant content and determine the best URL match."
        )
        log("search", f"Generated plan: {plan}")
        
        # Execute the plan
        if plan.startswith("FUNCTION_CALL:"):
            # Parse the function call
            log("search", "Parsing function call")
            tool_name, arguments = parse_function_call(plan)
            log("search", f"Parsed function call - Tool: {tool_name}, Arguments: {arguments}")
            
            if tool_name == "search_documents":
                # Get the search query from arguments
                search_query = arguments.get("query", query)
                log("search", f"Using search query: {search_query}")
                
                # Use FAISS to find relevant content
                log("search", "Generating embedding for search query")
                query_vec = get_embedding(search_query).reshape(1, -1)
                log("search", "Searching FAISS index")
                D, I = index.search(query_vec, 5)  # Get top 5 results
                log("search", f"FAISS search complete - Found {len(I[0])} potential matches")
                
                # Get all potential results
                potential_results = []
                for i, idx in enumerate(I[0]):
                    if idx < len(metadata):
                        result = metadata[idx].copy()
                        result['similarity'] = f"{float(100 / (1 + D[0][i])):.2f}%"
                        if 'chunk' not in result:
                            result['chunk'] = result.get('content', 'No content available')
                        potential_results.append(result)
                        log("search", f"Added potential result {i+1}: {result.get('url', 'No URL')} (Similarity: {result['similarity']})")
                
                if not potential_results:
                    log("search", "No potential results found")
                    return jsonify({
                        'query': query,
                        'results': [],
                        'total_results': 0
                    })
                
                # Let the agent process the results
                log("search", "Preparing context for agent")
                result_context = {
                    'query': query,
                    'results': potential_results,
                    'perception': perception.model_dump()
                }
                
                # Process through agent
                log("search", "Processing results through agent")
                agent_response = agent.process_input(str(result_context))
                log("search", f"Agent response: {agent_response}")
                
                # Parse the agent's response to get the best match
                if isinstance(agent_response, str):
                    log("search", "Parsing agent response for best match")
                    # Try to find the best match from the response
                    best_result = None
                    for result in potential_results:
                        if result['url'] in agent_response or result['chunk'] in agent_response:
                            best_result = result
                            log("search", f"Found best match in agent response: {result.get('url', 'No URL')}")
                            break
                    
                    if best_result:
                        # Store the search results in memory
                        log("search", "Storing search results in memory")
                        memory_item = MemoryItem(
                            text=f"Search results for: {query} - Best match: {best_result.get('url', 'No URL found')}",
                            type="tool_output",
                            tool_name="search_documents",
                            user_query=query,
                            tags=["search", "results", "best_match"]
                        )
                        memory_manager.add(memory_item)
                        
                        log("search", f"Returning best match: {best_result.get('url', 'No URL')}")
                        return jsonify({
                            'query': query,
                            'results': [best_result],
                            'total_results': 1
                        })
                
                best_result = potential_results[0]
                log("search", f"Selected top result: {best_result.get('url', 'No URL')}")
                
                # Store the search results in memory
                log("search", "Storing search results in memory")
                memory_item = MemoryItem(
                    text=f"Search results for: {query} - Best match: {best_result.get('url', 'No URL found')}",
                    type="tool_output",
                    tool_name="search_documents",
                    user_query=query,
                    tags=["search", "results", "best_match"]
                )
                memory_manager.add(memory_item)
                
                log("search", f"Returning top result: {best_result.get('url', 'No URL')}")
                return jsonify({
                    'query': query,
                    'results': [best_result],
                    'total_results': 1
                })
        
        # If no results found or plan failed
        log("search", "No results found or plan failed")
        return jsonify({
            'query': query,
            'results': [],
            'total_results': 0
        })
    
    except Exception as e:
        log("search", f"Error in search endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    ensure_faiss_ready()
    app.run(debug=True) 