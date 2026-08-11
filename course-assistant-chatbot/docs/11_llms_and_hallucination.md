# Language Models, Instruction Tuning, and Hallucination

A language model is trained to predict the next token in text. Scaled up and
trained on enough data, this simple objective produces systems that can
answer questions, summarize, and converse. Model size is measured in
parameters: flan-t5-base has about 250 million, TinyLlama about 1.1 billion,
and frontier commercial models are far larger.

Instruction tuning is additional training on examples of instructions and
good responses. It is why flan-t5-base follows a prompt like "Answer the
question using only the context below" instead of just continuing the text.
Flan-T5 is Google's instruction-tuned version of T5, an encoder-decoder
model well suited to reading provided text and producing an answer, which is
exactly the shape of the RAG generation step.

Hallucination is when a model generates fluent, confident, false statements.
It happens because the training objective rewards plausible text, not
verified truth: the model has no internal fact-checker. Small models
hallucinate more because they know less. Mitigations include retrieval
grounding (RAG), prompting the model to say "I don't know," and showing
sources so users can verify. None of these eliminates the problem; our
project treats hallucination as a design constraint to be managed rather
than a bug to be fixed.

Running models on a laptop CPU is practical below roughly one billion
parameters. flan-t5-base generates an answer in a few seconds on CPU, which
is acceptable for a course assistant, though users should be told the system
is working (visibility of system status).
