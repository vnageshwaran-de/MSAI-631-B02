# Group Project FAQ

Q: What is this project?
A: A course assistant chatbot for MSAI-631 that answers questions about the
syllabus and HCI study topics using retrieval-augmented generation. Ask it a
question and it retrieves relevant passages from the course documents and
generates an answer grounded in them, showing its sources.

Q: What are the five deliverables?
A: Proposal (1-2 pages), design document (3-5 pages), source code (git repo
plus zip), results paper (5-7 pages), and a presentation of at most 20
slides.

Q: What technology does it use?
A: Python. Gradio for the chat interface, sentence-transformers
(all-MiniLM-L6-v2) for embeddings, FAISS for similarity search, and
google/flan-t5-base via Hugging Face transformers for answer generation,
running on CPU PyTorch. Hosted on a free Hugging Face Space. No paid APIs.

Q: Why flan-t5-base and not a bigger model?
A: The project must run on a typical laptop and free hosting. flan-t5-base
is about 250M parameters, instruction-tuned, and answers from provided
context well. TinyLlama-1.1B-Chat and Qwen2.5-0.5B-Instruct were evaluated
as alternatives.

Q: Who is in the group?
A: Vinoth Nageshwaran, Parthiban Panneerselvam, and Saphalata Pathak. Lead
roles: data and retrieval pipeline, model testing and integration, and
interface and deployment, with everyone contributing to every deliverable.

Q: What can't the chatbot do?
A: It only knows the 10-20 documents in its knowledge base. It answers each
question independently (no conversation memory), and it declines to answer
when retrieval finds nothing relevant.
