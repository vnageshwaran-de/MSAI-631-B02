"""Unit tests for SentiBot (no server or Azure access required).

Run with:  python -m pytest test_bot.py -v

The Azure path is exercised with a fake analyzer so tests are
deterministic and network-free; the offline lexicon fallback is tested
directly.
"""

import re

from bot import SentimentBot
from sentiment import OfflineSentimentAnalyzer, SentimentUnavailable


class FakeAzureAnalyzer:
    """Stands in for AzureSentimentAnalyzer with canned responses."""

    def __init__(self, label="positive", fail=False):
        self.label = label
        self.fail = fail

    def analyze(self, text):
        if self.fail:
            raise SentimentUnavailable("simulated outage")
        scores = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
        if self.label in scores:
            scores[self.label] = 0.93
        return {"label": self.label, **scores}


def reply_for(text, bot=None):
    bot = bot or SentimentBot(FakeAzureAnalyzer(), "Azure AI Language (fake)")
    error = bot.validate(text)
    if error:
        return error
    intent, match = bot.interpret(text.strip())
    return bot.respond(intent, match, text.strip())


# ---------------- rule engine (unchanged behavior) ----------------

def test_greeting():
    assert "Hello" in reply_for("hi there")


def test_help_lists_capabilities_including_sentiment():
    reply = reply_for("what can you do?")
    assert "sentiment" in reply and "reverse" in reply


def test_time():
    assert re.search(r"\d{2}:\d{2}", reply_for("what time is it"))


def test_reverse_still_beats_greeting():
    assert "Reversed: dlrow olleh" in reply_for("reverse hello world")


def test_goodbye():
    assert "Goodbye" in reply_for("bye")


def test_empty_input_is_handled():
    assert "empty" in reply_for("   ")


def test_symbols_only_is_handled():
    assert "letters or numbers" in reply_for("@#$%^&*!!")


def test_too_long_input_is_handled():
    assert "too long" in reply_for("x" * 600)


# ---------------- AI service layer ----------------

def test_sentiment_command_reports_label_and_scores():
    reply = reply_for("sentiment I love this class")
    assert "positive" in reply and "0.93" in reply


def test_sentiment_command_beats_other_intents():
    # contains 'hello' but must still be a sentiment report
    reply = reply_for("sentiment hello darkness my old friend")
    assert "Sentiment for" in reply


def test_negative_mood_colors_fallback():
    bot = SentimentBot(FakeAzureAnalyzer(label="negative"), "fake")
    reply = reply_for("qwxzt flurble gibberish", bot)
    assert "frustration" in reply


def test_positive_mood_colors_fallback():
    bot = SentimentBot(FakeAzureAnalyzer(label="positive"), "fake")
    reply = reply_for("qwxzt flurble gibberish", bot)
    assert "positive energy" in reply


def test_service_outage_degrades_gracefully():
    bot = SentimentBot(FakeAzureAnalyzer(fail=True), "fake")
    reply = reply_for("sentiment I love this", bot)
    assert "unavailable" in reply
    # fallback replies still work with no mood prefix
    assert reply_for("qwxzt flurble", bot)


# ---------------- offline fallback backend ----------------

def test_offline_lexicon_positive():
    assert OfflineSentimentAnalyzer().analyze("I love this awesome class")["label"] == "positive"


def test_offline_lexicon_negative():
    assert OfflineSentimentAnalyzer().analyze("this is terrible and awful")["label"] == "negative"


def test_offline_lexicon_neutral():
    assert OfflineSentimentAnalyzer().analyze("the sky is blue")["label"] == "neutral"
