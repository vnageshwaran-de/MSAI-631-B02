# Retrieval-Augmented Generation (RAG)

Retrieval-augmented generation combines a search step with a text-generation
step. Instead of asking a language model a question directly and hoping its
training data contains the answer, a RAG system first retrieves relevant
passages from a document collection and then asks the model to compose an
answer from those passages.

The pipeline has an offline part and an online part. Offline, documents are
split into chunks, each chunk is converted into an embedding vector by a
sentence-embedding model, and the vectors are stored in a vector index.
Online, the user's question is embedded with the same model, the index
returns the nearest chunks by cosine similarity, and the chunks plus the
question are assembled into a prompt for the generation model.

RAG matters because language models hallucinate: when a model lacks
knowledge, it generates plausible-sounding text anyway, because generating
plausible text is literally what it is trained to do. Retrieval grounds the
generation in real documents, and small models benefit the most -- a 250M
parameter model like flan-t5-base knows very little about any specific
course, but it is quite good at reading provided passages and answering
from them.

The approach was formalized by Lewis et al. (2020) at Facebook AI Research.
Practical RAG quality depends heavily on unglamorous details: chunk size,
chunk overlap, how many passages to retrieve, and what to do when retrieval
finds nothing relevant (the honest answer is to say "I don't know").
