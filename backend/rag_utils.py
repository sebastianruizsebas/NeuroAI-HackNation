import json
import os
from typing import Dict, List, Tuple
import re

def load_all_chunks(chunk_paths: list) -> Dict[str, List[str]]:
    """Load and merge chunks from multiple JSON files (supports both dict and list formats)."""
    all_chunks = {}
    for path in chunk_paths:
        with open(path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
            # If chunks is a list of dicts (file, chunk), convert to dict[str, list[str]]
            if isinstance(chunks, list):
                for entry in chunks:
                    fname = entry['file']
                    chunk = entry['chunk']
                    all_chunks.setdefault(fname, []).append(chunk)
            else:
                for fname, chunk_list in chunks.items():
                    all_chunks.setdefault(fname, []).extend(chunk_list)
    return all_chunks

CHUNKS_PATH = os.path.join(os.path.dirname(__file__), 'math_ml_chunks.json')

def load_chunks(chunks_path: str = CHUNKS_PATH) -> Dict[str, List[str]]:
    with open(chunks_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_relevant_chunks(query: str, chunks: Dict[str, List[str]], top_k: int = 3) -> List[Tuple[str, str]]:
    """Return top_k (filename, chunk) pairs most relevant to the query (simple keyword match)."""
    query_words = set(re.findall(r'\w+', query.lower()))
    scored_chunks = []
    for fname, chunk_list in chunks.items():
        for chunk in chunk_list:
            chunk_words = set(re.findall(r'\w+', chunk.lower()))
            score = len(query_words & chunk_words)
            if score > 0:
                scored_chunks.append((score, fname, chunk))
    # Sort by score descending
    scored_chunks.sort(reverse=True)
    return [(fname, chunk) for score, fname, chunk in scored_chunks[:top_k]]

if __name__ == "__main__":
    # Example usage: load and merge both math_ml_chunks.json and mit_ocw_chunks.json
    base_dir = os.path.dirname(__file__)
    chunk_files = [
        os.path.join(base_dir, 'math_ml_chunks.json'),
        os.path.join(base_dir, 'mit_ocw_chunks.json'),
    ]
    chunks = load_all_chunks(chunk_files)
    query = input("Enter a topic or query: ")
    results = find_relevant_chunks(query, chunks)
    for fname, chunk in results:
        print(f"From {fname}:\n{chunk}\n{'-'*40}")
