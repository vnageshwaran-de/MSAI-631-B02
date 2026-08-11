# MSAI-631 Course Assistant Chatbot (RAG)

Group project for MSAI-631-B02, Artificial Intelligence for Human-Computer
Interaction. University of the Cumberlands, 2026 Summer, Second Bi-term.

Group: Vinoth Nageshwaran, Parthiban Panneerselvam, Saphalata Pathak

## What it is

A chatbot that answers questions about our course material using
retrieval-augmented generation (RAG). Questions are matched against a small
knowledge base of course documents (in `docs/`) using sentence embeddings and
FAISS similarity search, and google/flan-t5-base writes an answer from the
retrieved passages. Every answer shows the source passages it used. Free
tools only -- no OpenAI or paid APIs.

## How to run it

```bash
pip install -r requirements.txt
python ingest.py     # builds index.faiss + chunks.pkl from docs/ (~1 min)
python app.py        # starts the Gradio chat UI at http://localhost:7860
```

First run downloads the models from Hugging Face (about 1 GB total for
flan-t5-base + all-MiniLM-L6-v2). Everything runs on CPU; a typical laptop
answers a question in a few seconds.

`python eval.py` runs our 20 test questions through the pipeline and prints
answers, retrieval scores, and timings. `python eval.py MODEL_ID` does the
same with a different generation model (we used this to compare
flan-t5-base against TinyLlama-1.1B-Chat and Qwen2.5-0.5B-Instruct).

## Files

- `app.py` -- the Gradio chat app and the RAG pipeline (retrieve, prompt, generate)
- `ingest.py` -- chunks the documents and builds the FAISS index
- `eval.py` -- test-question harness used for model comparison and threshold tuning
- `docs/` -- the knowledge base: course syllabus summary + HCI study notes we wrote
- `requirements.txt` -- Python dependencies

## Credits for reused code

As required by the assignment, sources we started from:

- The Gradio chatbot example linked in the project instructions
  (kdnuggets.com "Build an AI Chatbot in 5 Minutes with Hugging Face and
  Gradio"). We kept the Gradio + Hugging Face structure and replaced its
  DialoGPT model with a full RAG pipeline (embeddings, FAISS retrieval,
  similarity threshold, prompt template, source display).
- `gr.ChatInterface` usage from the Gradio documentation.
- The semantic-search pattern (encode, normalize, inner-product search) from
  the sentence-transformers documentation examples.

All other code, the chunking logic, the threshold mechanism, the evaluation
harness, and all documents in `docs/` were written by the group.

## Known issues / notes

- The Space goes to sleep on the free tier; the first question after idle is
  slow (model reload).
- Answers are short -- that is flan-t5-base being a 250M-parameter model.
- Each question is answered independently; there is no conversation memory.
- If the similarity of the best retrieved passage is below 0.35, the bot
  says it does not know rather than answering from irrelevant text.
