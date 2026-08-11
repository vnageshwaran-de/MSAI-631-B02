# Text Embeddings and Similarity Search

A text embedding is a fixed-length vector of numbers that represents the
meaning of a piece of text. Texts with similar meanings get vectors that
point in similar directions, so semantic similarity becomes a geometry
problem: measure the cosine of the angle between two vectors. Cosine
similarity of 1.0 means identical direction; near 0 means unrelated.

Sentence-embedding models like all-MiniLM-L6-v2 are trained so that
paraphrases land close together. MiniLM produces 384-dimensional vectors, is
about 80 MB, and encodes hundreds of sentences per second on a laptop CPU,
which is why it is the default choice for small RAG projects. This is
different from keyword search: "When is the assignment due?" and "submission
deadline" share no words but land close in embedding space.

FAISS (Facebook AI Similarity Search) is a library for finding the nearest
vectors to a query vector efficiently. For millions of vectors it offers
approximate indexes that trade a little accuracy for a lot of speed. At the
scale of our project -- a few hundred vectors -- an exact flat index
(IndexFlatIP or IndexFlatL2) searches in under a millisecond, so
approximation is unnecessary.

One practical detail: if vectors are normalized to length 1, inner product
equals cosine similarity, which is why RAG code commonly normalizes
embeddings and uses an inner-product index.
