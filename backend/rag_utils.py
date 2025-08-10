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
    """Return top_k (filename, chunk) pairs most relevant to the query with improved scoring."""
    # Enhanced keyword extraction and scoring
    query_lower = query.lower()
    query_words = set(re.findall(r'\w+', query_lower))
    
    # Extract important technical terms and phrases for better matching
    important_terms = []
    technical_patterns = [
        r'\b(?:neural networks?|machine learning|deep learning|classification|regression)\b',
        r'\b(?:gradient descent|optimization|convex|linear algebra|calculus)\b',
        r'\b(?:statistics|probability|bayesian|risk|loss function)\b',
        r'\b(?:svm|support vector|boosting|ensemble|random forest)\b',
        r'\b(?:clustering|dimensionality|feature|supervised|unsupervised)\b'
    ]
    
    for pattern in technical_patterns:
        matches = re.findall(pattern, query_lower)
        important_terms.extend(matches)
    
    scored_chunks = []
    for fname, chunk_list in chunks.items():
        for chunk in chunk_list:
            chunk_lower = chunk.lower()
            chunk_words = set(re.findall(r'\w+', chunk_lower))
            
            # Multi-level scoring system
            word_overlap_score = len(query_words & chunk_words)
            
            # Bonus for exact phrase matches
            phrase_bonus = 0
            for term in important_terms:
                if term in chunk_lower:
                    phrase_bonus += 5  # Higher weight for technical terms
            
            # Bonus for key concept matches
            concept_bonus = 0
            key_concepts = ['learning', 'algorithm', 'model', 'training', 'prediction', 'error', 'optimization']
            for concept in key_concepts:
                if concept in query_lower and concept in chunk_lower:
                    concept_bonus += 2
            
            # Penalty for very short chunks (less informative)
            length_factor = min(1.0, len(chunk) / 200)  # Normalize around 200 chars
            
            final_score = (word_overlap_score + phrase_bonus + concept_bonus) * length_factor
            
            if final_score > 0:
                scored_chunks.append((final_score, fname, chunk))
    
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
