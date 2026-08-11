# eval.py
# Runs our set of test questions through the retrieval + generation
# pipeline and prints the answers, retrieval scores, and timing.
# We used this to (a) compare candidate models and (b) pick the
# MIN_SIMILARITY threshold in app.py.
#
# Usage: python eval.py            (uses flan-t5-base)
#        python eval.py MODEL_ID   (e.g. TinyLlama/TinyLlama-1.1B-Chat-v1.0)

import pickle
import sys
import time

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

GEN_MODEL = sys.argv[1] if len(sys.argv) > 1 else "google/flan-t5-base"

TEST_QUESTIONS = [
    # answerable from the knowledge base
    "What is Fitts's Law?",
    "What are Nielsen's ten usability heuristics?",
    "What is the difference between formative and summative evaluation?",
    "What is a heuristic evaluation?",
    "What does WIMP stand for?",
    "What is the gulf of execution?",
    "What is the gulf of evaluation?",
    "What is retrieval-augmented generation?",
    "Why do chatbots hallucinate?",
    "What is a conversational interface?",
    "What are the five project deliverables?",
    "What models does the group project use?",
    "What is affordance in interface design?",
    "What is Hick's Law?",
    "What is the think-aloud protocol?",
    "What is cognitive load in HCI?",
    # NOT answerable -- should trigger the "I don't know" response
    "What is the capital of France?",
    "Who won the World Cup?",
    "How do I make lasagna?",
    "What is the stock price of Apple?",
]

print("Loading index, embedder, and", GEN_MODEL)
index = faiss.read_index("index.faiss")
with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
tokenizer = AutoTokenizer.from_pretrained(GEN_MODEL)
gen_model = AutoModelForSeq2SeqLM.from_pretrained(GEN_MODEL)

for q in TEST_QUESTIONS:
    t0 = time.time()
    q_vec = embedder.encode([q], convert_to_numpy=True,
                            normalize_embeddings=True).astype(np.float32)
    scores, ids = index.search(q_vec, 3)
    best = scores[0][0]
    context = "\n\n".join(chunks[i]["text"] for i in ids[0] if i != -1)
    prompt = (
        "Answer the question using only the context below. "
        "If the context does not contain the answer, say you don't know.\n\n"
        f"Context:\n{context}\n\nQuestion: {q}\n\nAnswer:"
    )
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True,
                       max_length=1024)
    output_ids = gen_model.generate(**inputs, max_new_tokens=200)
    out = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    dt = time.time() - t0
    print(f"\nQ: {q}")
    print(f"   best similarity: {best:.3f}   time: {dt:.1f}s")
    print(f"   A: {out}")
