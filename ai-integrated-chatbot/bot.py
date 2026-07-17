# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
AI-integrated chatbot built on the Microsoft Bot Framework.

This bot started life as the rule-based TradBot from the Prototype Simple
Traditional Chatbot assignment (../traditional-chatbot). The rule engine
is unchanged; what is new is the sentiment layer. Every user message is
sent to a sentiment analyzer -- Azure AI Language (Text Analytics) when
credentials are configured, or a small offline lexicon otherwise -- and
the bot adapts its tone to the detected sentiment. There is also an
explicit `sentiment <text>` command that reports the raw scores.
"""

import random
import re
from datetime import datetime

from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount

from sentiment import OfflineSentimentAnalyzer, SentimentUnavailable

BOT_NAME = "SentiBot"

CAPABILITIES = (
    "Here is what I can do:\n"
    "1. **greet** - say hi/hello and I will greet you back\n"
    "2. **help** - type 'help' or 'what can you do' to see this list\n"
    "3. **time / date** - ask 'what time is it' or 'what is today's date'\n"
    "4. **reverse <text>** - I will reverse any text you give me\n"
    "5. **sentiment <text>** - I will analyze the feeling in your text "
    "using Azure AI Language\n"
    "6. **joke** - ask me to tell you a joke\n"
    "7. **about** - ask 'who are you' to learn about me\n"
    "8. **bye** - say goodbye to end our chat\n\n"
    "I also quietly read the mood of everything you type and adjust my "
    "tone. Try telling me something happy or something sad!"
)

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the chatbot go to therapy? It had too many unresolved issues.",
    "I would tell you a UDP joke, but you might not get it.",
    "There are only 10 kinds of people: those who understand binary and those who don't.",
]

FALLBACKS = [
    "I'm sorry, I did not understand that. Type **help** to see what I can do.",
    "Hmm, that doesn't match anything I know. Try **help** for a list of my capabilities.",
    "I couldn't make sense of that. Type **help** to see examples of what I understand.",
]

# Tone prefixes keyed by detected sentiment, used to color the fallback
# and thanks/goodbye responses.
MOOD_PREFIXES = {
    "positive": "Love the positive energy! ",
    "negative": "I'm sensing some frustration -- sorry about that. ",
    "mixed": "Sounds like mixed feelings. ",
}


class SentimentBot(ActivityHandler):
    """Rule-based bot with an AI-as-a-service sentiment layer."""

    INTENTS = [
        # Anchored, payload-carrying commands FIRST (see traditional-chatbot:
        # 'reverse hello world' contains 'hello' and would otherwise be
        # swallowed by the greeting intent).
        ("sentiment", re.compile(r"^(sentiment|analyze|mood)\s+(?P<payload>.+)$", re.I)),
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

    def __init__(self, analyzer=None, backend_name: str = "offline lexicon"):
        self.analyzer = analyzer or OfflineSentimentAnalyzer()
        self.backend_name = backend_name

    # ------------------------------------------------------------------ #
    # NLU layer (unchanged from traditional-chatbot)                      #
    # ------------------------------------------------------------------ #
    def interpret(self, text: str):
        for intent, pattern in self.INTENTS:
            match = pattern.search(text)
            if match:
                return intent, match
        return "unknown", None

    def validate(self, text: str):
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

    # ------------------------------------------------------------------ #
    # AI-as-a-service layer                                               #
    # ------------------------------------------------------------------ #
    def get_sentiment(self, text: str):
        """Return a sentiment dict, or None if the service is unavailable."""
        try:
            return self.analyzer.analyze(text)
        except SentimentUnavailable:
            return None

    def sentiment_report(self, payload: str) -> str:
        result = self.get_sentiment(payload)
        if result is None:
            return ("Sorry, the sentiment service is unavailable right now. "
                    "Please try again in a moment.")
        return (
            f"Sentiment for \"{payload}\": **{result['label']}**\n"
            f"(positive {result['positive']:.2f} / "
            f"neutral {result['neutral']:.2f} / "
            f"negative {result['negative']:.2f})\n"
            f"[analyzed by {self.backend_name}]"
        )

    def mood_prefix(self, text: str) -> str:
        """A tone-adjusting prefix based on the message's sentiment."""
        result = self.get_sentiment(text)
        if result is None:
            return ""
        return MOOD_PREFIXES.get(result["label"], "")

    # ------------------------------------------------------------------ #
    # Response synthesis                                                  #
    # ------------------------------------------------------------------ #
    def respond(self, intent: str, match, text: str) -> str:
        if intent == "sentiment":
            return self.sentiment_report(match.group("payload"))
        if intent == "greeting":
            return (f"Hello! I'm {BOT_NAME}, a rule-based chatbot with an "
                    "AI mood sensor. Type **help** to see what I can do.")
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
            return (f"I am {BOT_NAME}, built for MSAI-631. My conversation "
                    "logic is traditional rule-based pattern matching, but I "
                    "use a cloud AI service (Azure AI Language) to understand "
                    f"how you feel. Current sentiment backend: {self.backend_name}.")
        if intent == "thanks":
            return self.mood_prefix(text) + \
                "You're welcome! Anything else? Type **help** for options."
        if intent == "goodbye":
            return self.mood_prefix(text) + "Goodbye! Thanks for chatting with me."
        # Unknown intent: let the AI service color the fallback so the bot
        # still responds to the *feeling* of a message it cannot parse.
        return self.mood_prefix(text) + random.choice(FALLBACKS)

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
                    f"Welcome! I'm {BOT_NAME} -- a rule-based chatbot with an "
                    "Azure AI-powered mood sensor. Type **help** to see my "
                    "capabilities, or just tell me how your day is going."
                )
