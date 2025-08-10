import os
from pdf_chunker import extract_text_from_pdf, chunk_text

READINGS_DIR = os.path.join(os.path.dirname(__file__), 'readings')
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), 'mit_ocw_chunks.json')


all_chunks = []
for fname in os.listdir(READINGS_DIR):
    if fname.lower().endswith('.pdf'):
        pdf_path = os.path.join(READINGS_DIR, fname)
        print(f'Extracting text from {pdf_path}...')
        text = extract_text_from_pdf(pdf_path, method='pdfplumber')
        chunks = chunk_text(text, max_chunk_size=500)
        for chunk in chunks:
            all_chunks.append({'file': fname, 'chunk': chunk})

import json
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(all_chunks, f, indent=2, ensure_ascii=False)

print(f"Done. Extracted {len(all_chunks)} chunks to {OUTPUT_JSON}")
