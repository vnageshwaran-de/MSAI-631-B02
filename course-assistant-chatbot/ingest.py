# ingest.py
# Builds the FAISS index from the documents in docs/.
# Run this once before starting the app, and re-run it whenever
# the documents change:  python ingest.py
#
# MSAI-631-B02 Group Project
# Vinoth Nageshwaran, Parthiban Panneerselvam, Saphalata Pathak
#
# The chunking approach (fixed-size word chunks with overlap) is a
# standard pattern; we adapted the general structure from the
# sentence-transformers semantic search examples:
# https://www.sbert.net/examples/applications/semantic-search/README.html

import json
import os
import pickle

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DOCS_DIR = "docs"
INDEX_FILE = "index.faiss"
CHUNKS_FILE = "chunks.pkl"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_WORDS = 250   # target words per chunk
OVERLAP_WORDS = 50  # overlap between consecutive chunks


def chunk_text(text, source):
    """Split one document into overlapping word chunks.

    We keep an overlap so a sentence near a boundary still has some
    context in at least one chunk. 250/50 came from trying a few values
    against our test questions (see eval.py).
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        piece = words[start:start + CHUNK_WORDS]
        if len(piece) < 30 and chunks:
            # tail is tiny -- glue it onto the previous chunk instead
            chunks[-1]["text"] += " " + " ".join(piece)
            break
        chunks.append({"text": " ".join(piece), "source": source})
        start += CHUNK_WORDS - OVERLAP_WORDS
    return chunks


def load_documents():
    """Read every .md / .txt file in docs/ and chunk it."""
    all_chunks = []
    for name in sorted(os.listdir(DOCS_DIR)):
        if not name.endswith((".md", ".txt")):
            continue
        path = os.path.join(DOCS_DIR, name)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        # strip the most common markdown noise; we don't need a full parser
        cleaned = []
        for line in text.splitlines():
            line = line.replace("#", "").replace("*", "").strip()
            if line:
                cleaned.append(line)
        all_chunks.extend(chunk_text(" ".join(cleaned), source=name))
    return all_chunks


def main():
    print("Loading documents from", DOCS_DIR)
    chunks = load_documents()
    print(f"  {len(chunks)} chunks from the knowledge base")

    print("Loading embedding model", EMBED_MODEL)
    model = SentenceTransformer(EMBED_MODEL)

    print("Embedding chunks (this takes a minute on CPU)...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True,
                              convert_to_numpy=True, normalize_embeddings=True)

    # Normalized vectors + inner product = cosine similarity.
    # IndexFlatIP does exact search, which is fine at our scale
    # (a few hundred vectors).
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype(np.float32))

    faiss.write_index(index, INDEX_FILE)
    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump(chunks, f)

    print(f"Saved {INDEX_FILE} ({index.ntotal} vectors, dim={dim}) and {CHUNKS_FILE}")


if __name__ == "__main__":
    main()
