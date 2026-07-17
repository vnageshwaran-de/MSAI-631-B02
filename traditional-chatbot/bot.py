# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Rule-based (traditional) chatbot built on the Microsoft Bot Framework.

The bot uses deterministic pattern matching (regular expressions) to map
user utterances to intents -- no machine learning or LLMs involved. The
intent table is ordered by priority; the first pattern that matches wins.
Unrecognized or malformed input falls through to a graceful fallback
handler that guides the user back to supported capabilities.

The design keeps the NLU layer isolated in `interpret()`, so the rule
engine could later be swapped for an AI-as-a-service offering such as
Azure Cognitive Services (CLU/LUIS) without touching the plumbing.
"""

import random
import re
from datetime import datetime

from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount

BOT_NAME = "TradBot"

CAPABILITIES = (
    "Here is what I can do:\n"
    "1. **greet** - say hi/hello and I will greet you back\n"
    "2. **help** - type 'help' or 'what can you do' to see this list\n"
    "3. **time / date** - ask 'what time is it' or 'what is today's date'\n"
    "4. **reverse <text>** - I will reverse any text you give me\n"
    "5. **joke** - ask me to tell you a joke\n"
    "6. **about** - ask 'who are you' to learn about me\n"
    "7. **bye** - say goodbye to end our chat\n\n"
    "I am a traditional rule-based bot, so please phrase requests simply!"
)

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the chatbot go to therapy? It had too many unresolved issues.",
    "I would tell you a UDP joke, but you might not get it.",
    "There are only 10 kinds of people: those who understand binary and those who don't.",
]

FALLBACKS = [
    "I'm sorry, I did not understand that. I am a simple rule-based bot. "
    "Type **help** to see what I can do.",
    "Hmm, that input doesn't match anything I know. Try **help** for a "
    "list of my capabilities.",
    "I couldn't make sense of that. Remember, I only understand simple "
    "phrases -- type **help** to see examples.",
]


class RuleBasedBot(ActivityHandler):
    """Traditional pattern-matching chatbot."""

    # Ordered intent table: (intent_name, compiled_pattern)
    INTENTS = [
        # 'reverse <text>' is anchored and carries a payload, so it must be
        # checked FIRST: e.g. 'reverse hello world' contains 'hello' and
        # would otherwise be swallowed by the greeting intent.
        ("reverse", re.compile(r"^reverse\s+(?P<payload>.+)$", re.I)),
        ("goodbye", re.compile(r"\b(bye|goodbye|see you|quit|exit)\b", re.I)),
        ("greeting", re.compile(r"\b(hi|hello|hey|good (morning|afternoon|evening)|greetings)\b", re.I)),
        ("help", re.compile(r"\b(help|capabilit|what can you do|commands|options|menu)\b", re.I)),
        ("time", re.compile(r"\b(time)\b", re.I)),
        ("date", re.compile(r"\b(date|today|day is it)\b", re.I)),
        ("joke", re.compile(r"\b(joke|funny|laugh)\b", re.I)),
        ("about", re.compile(r"\b(who are you|about you|your name|what are you)\b", re.I)),
        ("thanks", re.compile(r"\b(thanks|thank you|thx)\b", re.I)),
    ]

    MAX_INPUT_LENGTH = 500

    # ------------------------------------------------------------------ #
    # NLU layer: maps raw text to (intent, match). Replace this method    #
    # with a call to Azure Cognitive Services CLU/LUIS to upgrade the bot #
    # to ML-based understanding without changing anything else.           #
    # ------------------------------------------------------------------ #
    def interpret(self, text: str):
        for intent, pattern in self.INTENTS:
            match = pattern.search(text)
            if match:
                return intent, match
        return "unknown", None

    def validate(self, text: str):
        """Guard against malformed input. Returns an error reply or None."""
        if text is None or not text.strip():
            return ("You sent an empty message. Please type something -- "
                    "for example, **help**.")
        if len(text) > self.MAX_INPUT_LENGTH:
            return (f"That message is too long for me "
                    f"({len(text)} characters; my limit is "
                    f"{self.MAX_INPUT_LENGTH}). Please keep it short.")
        if not re.search(r"[A-Za-z0-9]", text):
            return ("I can only process text containing letters or numbers. "
                    "Type **help** to see what I understand.")
        return None

    def respond(self, intent: str, match, text: str) -> str:
        if intent == "greeting":
            return (f"Hello! I'm {BOT_NAME}, a traditional rule-based "
                    "chatbot. Type **help** to see what I can do.")
        if intent == "help":
            return CAPABILITIES
        if intent == "time":
            return f"The current time is {datetime.now().strftime('%I:%M %p')}."
        if intent == "date":
            return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
        if intent == "reverse":
            payload = match.group("payload")
            return f"Reversed: {payload[::-1]}"
        if intent == "joke":
            return random.choice(JOKES)
        if intent == "about":
            return (f"I am {BOT_NAME}, a simple chatbot built with the "
                    "Microsoft Bot Framework for MSAI-631. I use "
                    "rule-based pattern matching -- no machine learning! "
                    "But my design allows me to be extended with services "
                    "like Azure Cognitive Services.")
        if intent == "thanks":
            return "You're welcome! Anything else? Type **help** for options."
        if intent == "goodbye":
            return "Goodbye! Thanks for chatting with me."
        return random.choice(FALLBACKS)

    async def on_message_activity(self, turn_context: TurnContext):
        text = turn_context.activity.text

        error = self.validate(text)
        if error:
            await turn_context.send_activity(MessageFactory.text(error))
            return

        intent, match = self.interpret(text.strip())
        reply = self.respond(intent, match, text.strip())
        await turn_context.send_activity(MessageFactory.text(reply))

    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    f"Welcome! I'm {BOT_NAME} \U0001F916 -- a traditional "
                    "rule-based chatbot. Type **help** to see my capabilities."
                )
