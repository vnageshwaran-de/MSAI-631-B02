# app.py
# Course assistant chatbot using retrieval-augmented generation (RAG).
# Runs as a Gradio app, deployable to a free Hugging Face Space.
#
# MSAI-631-B02 Group Project
# Vinoth Nageshwaran, Parthiban Panneerselvam, Saphalata Pathak
#
# Credits / sources we started from (as required by the assignment):
# - Basic Gradio chatbot structure adapted from:
#   https://www.kdnuggets.com/2023/06/build-ai-chatbot-5-minutes-hugging-face-gradio.html
#   (the example linked in the project instructions -- we replaced its
#   DialoGPT model with a full RAG pipeline)
# - gr.ChatInterface usage from the Gradio docs:
#   https://www.gradio.app/docs/gradio/chatinterface
# - transformers pipeline usage from the Hugging Face docs:
#   https://huggingface.co/docs/transformers/main_classes/pipelines
#
# Run `python ingest.py` first to build the index.

import pickle

import faiss
import gradio as gr
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GEN_MODEL = "google/flan-t5-base"

TOP_K = 3
# If the best cosine similarity is below this, we say "I don't know"
# instead of answering from irrelevant passages. We originally guessed
# 0.35, but our test questions showed real course questions can score
# as low as ~0.23 (e.g. "What is the gulf of execution?") while
# off-topic questions stay near 0.10, so 0.20 separates them cleanly.
# See eval.py and the results paper.
MIN_SIMILARITY = 0.20

print("Loading index and chunks...")
index = faiss.read_index("index.faiss")
with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

print("Loading embedding model...")
embedder = SentenceTransformer(EMBED_MODEL)

print("Loading generation model (first run downloads ~1 GB)...")
# Note: we first used pipeline("text2text-generation", ...) like the
# tutorials show, but that task name was removed in transformers v5,
# so we load the model and tokenizer explicitly. This works on both
# transformers 4.x and 5.x.
tokenizer = AutoTokenizer.from_pretrained(GEN_MODEL)
gen_model = AutoModelForSeq2SeqLM.from_pretrained(GEN_MODEL)


def generate(prompt, max_new_tokens=200):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True,
                       max_length=1024)
    output_ids = gen_model.generate(**inputs, max_new_tokens=max_new_tokens)
    return tokenizer.decode(output_ids[0], skip_special_tokens=True)


def retrieve(question):
    """Return the top-k chunks for a question, with scores."""
    q_vec = embedder.encode([question], convert_to_numpy=True,
                            normalize_embeddings=True).astype(np.float32)
    scores, ids = index.search(q_vec, TOP_K)
    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx == -1:
            continue
        results.append({"score": float(score), **chunks[idx]})
    return results


def build_prompt(question, passages):
    context = "\n\n".join(p["text"] for p in passages)
    return (
        "Answer the question using only the context below. "
        "If the context does not contain the answer, say you don't know.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\nAnswer:"
    )


def answer(message, history):
    """Gradio ChatInterface callback. History is unused for now --
    each question is answered independently (a known limitation we
    discuss in the design document)."""
    passages = retrieve(message)

    if not passages or passages[0]["score"] < MIN_SIMILARITY:
        return ("Sorry, I don't have information on that in the course "
                "documents. Try asking about the syllabus or an HCI topic "
                "covered in class.")

    prompt = build_prompt(message, passages)
    result = generate(prompt)

    # Show which passages the answer came from, so the user can verify.
    sources = "\n".join(
        f"- {p['source']} (similarity {p['score']:.2f})" for p in passages
    )
    return f"{result}\n\n**Sources used:**\n{sources}"


demo = gr.ChatInterface(
    fn=answer,
    title="MSAI-631 Course Assistant",
    description=(
        "Ask me about the course syllabus or the HCI topics in the study "
        "notes. I answer only from the course documents, and I show my "
        "sources. Built with flan-t5-base + FAISS + all-MiniLM-L6-v2."
    ),
    examples=[
        "What is Fitts's Law?",
        "What are Nielsen's usability heuristics?",
        "How is the group project graded?",
        "What is retrieval-augmented generation?",
    ],
)

if __name__ == "__main__":
    demo.launch()
