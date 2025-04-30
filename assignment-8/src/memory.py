# memory.py

import numpy as np
import faiss
import requests
from typing import List, Optional, Literal
from pydantic import BaseModel
from datetime import datetime
import json
from pathlib import Path
import os


class MemoryItem(BaseModel):
    text: str
    type: Literal["preference", "tool_output", "fact", "query", "system"] = "fact"
    timestamp: Optional[str] = datetime.now().isoformat()
    tool_name: Optional[str] = None
    user_query: Optional[str] = None
    tags: List[str] = []
    session_id: Optional[str] = None
    url: Optional[str] = None
    chunk_id: Optional[str] = None


class MemoryManager:
    def __init__(self, embedding_model_url="http://localhost:11434/api/embeddings", model_name="nomic-embed-text"):
        self.embedding_model_url = embedding_model_url
        self.model_name = model_name
        self.index = None
        self.data: List[MemoryItem] = []
        self.embeddings: List[np.ndarray] = []
        self.index_path = Path("faiss_index")
        self.metadata_path = self.index_path / "metadata.json"
        self._load_index()

    def _load_index(self):
        """Load existing FAISS index and metadata if available"""
        try:
            if self.index_path.exists():
                self.index = faiss.read_index(str(self.index_path / "index.bin"))
                if self.metadata_path.exists():
                    with open(self.metadata_path, 'r') as f:
                        self.data = [MemoryItem(**item) for item in json.load(f)]
        except Exception as e:
            print(f"Error loading index: {e}")
            self.index = None
            self.data = []

    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text using the embedding model"""
        response = requests.post(
            self.embedding_model_url,
            json={"model": self.model_name, "prompt": text}
        )
        response.raise_for_status()
        return np.array(response.json()["embedding"], dtype=np.float32)

    def add(self, item: MemoryItem):
        """Add a new memory item to the index"""
        emb = self._get_embedding(item.text)
        self.embeddings.append(emb)
        self.data.append(item)

        # Initialize or add to index
        if self.index is None:
            self.index = faiss.IndexFlatL2(len(emb))
        self.index.add(np.stack([emb]))

        # Save index and metadata
        self._save_index()

    def _save_index(self):
        """Save the FAISS index and metadata"""
        self.index_path.mkdir(exist_ok=True)
        if self.index:
            faiss.write_index(self.index, str(self.index_path / "index.bin"))
        with open(self.metadata_path, 'w') as f:
            json.dump([item.dict() for item in self.data], f, indent=2)

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        type_filter: Optional[str] = None,
        tag_filter: Optional[List[str]] = None,
        session_filter: Optional[str] = None
    ) -> List[MemoryItem]:
        """Retrieve relevant memories based on query"""
        if not self.index or len(self.data) == 0:
            return []

        query_vec = self._get_embedding(query).reshape(1, -1)
        D, I = self.index.search(query_vec, top_k * 2)  # Overfetch to allow filtering

        results = []
        for idx in I[0]:
            if idx >= len(self.data):
                continue
            item = self.data[idx]

            # Filter by type
            if type_filter and item.type != type_filter:
                continue

            # Filter by tags
            if tag_filter and not any(tag in item.tags for tag in tag_filter):
                continue

            # Filter by session
            if session_filter and item.session_id != session_filter:
                continue

            results.append(item)
            if len(results) >= top_k:
                break

        return results

    def bulk_add(self, items: List[MemoryItem]):
        """Add multiple memory items at once"""
        for item in items:
            self.add(item)
