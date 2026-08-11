# Conversational Interfaces and Chatbots

A conversational interface lets users interact with a system through natural
language, typed or spoken, instead of buttons and menus. Chatbots are the
text form; voice assistants like Alexa and Siri are the spoken form.

Early chatbots were rule-based. ELIZA (1966) used pattern matching to
imitate a psychotherapist and showed how readily people attribute
understanding to machines (the "ELIZA effect"). Later systems used intent
classification: map the user's utterance to one of a fixed set of intents,
then run a scripted response. This works for narrow tasks like checking a
bank balance but breaks on anything unanticipated.

Modern chatbots use large language models that generate free-form responses.
They handle open-ended language well, but introduce new HCI problems: they
can hallucinate confident falsehoods, their capabilities are opaque to
users, and errors are hard to recognize because the prose is fluent.

Design guidelines for conversational UIs include: make the system's scope
clear up front, provide example prompts, show what the system is doing
(typing indicators, progress), make errors recoverable, and ground answers
in verifiable sources when accuracy matters. Retrieval-augmented generation
is the standard grounding technique, and displaying the retrieved sources --
as our course assistant does -- turns the opaque generation step into
something the user can check.
