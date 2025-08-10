import pdfplumber
import os
import json
from typing import List, Dict
from pathlib import Path
import PyPDF2


def extract_text_from_pdf(pdf_path: str, method: str = 'auto') -> str:
    """Extract all text from a PDF file. Use pdfplumber if available, fallback to PyPDF2."""
    text = ""
    if method == 'pdfplumber' or method == 'auto':
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            if text.strip():
                return text
        except Exception as e:
            print(f"pdfplumber failed: {e}")
            if method == 'pdfplumber':
                return ""
    # fallback to PyPDF2
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"PyPDF2 failed: {e}")
    return text

def chunk_text(text: str, max_chunk_size: int = 1000) -> List[str]:
    """Split text into chunks of approximately max_chunk_size characters."""
    words = text.split()
    chunks = []
    chunk = []
    current_len = 0
    for word in words:
        if current_len + len(word) + 1 > max_chunk_size:
            chunks.append(' '.join(chunk))
            chunk = []
            current_len = 0
        chunk.append(word)
        current_len += len(word) + 1
    if chunk:
        chunks.append(' '.join(chunk))
    return chunks

def process_pdf_folder(folder_path: str, output_json: str, max_chunk_size: int = 1000):
    """Extract and chunk all PDFs in a folder, save as JSON."""
    pdf_files = list(Path(folder_path).glob('*.pdf'))
    all_chunks: Dict[str, List[str]] = {}
    for pdf_file in pdf_files:
        print(f"Processing {pdf_file.name}...")
        text = extract_text_from_pdf(str(pdf_file))
        chunks = chunk_text(text, max_chunk_size)
        all_chunks[pdf_file.name] = chunks
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    print(f"Saved chunked data to {output_json}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Chunk all PDFs in a folder.")
    parser.add_argument('folder', help='Folder containing PDF files')
    parser.add_argument('--output', default='pdf_chunks.json', help='Output JSON file')
    parser.add_argument('--chunk_size', type=int, default=1000, help='Max chunk size in characters')
    args = parser.parse_args()
    process_pdf_folder(args.folder, args.output, args.chunk_size)
