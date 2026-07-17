"""Unit tests for the rule-based logic in bot.py (no server required).

Run with:  python -m pytest test_bot.py -v
"""

import re

from bot import RuleBasedBot


BOT = RuleBasedBot()


def reply_for(text: str) -> str:
    """Helper: run validation + interpretation + response synchronously."""
    error = BOT.validate(text)
    if error:
        return error
    intent, match = BOT.interpret(text.strip())
    return BOT.respond(intent, match, text.strip())


def test_greeting():
    assert "Hello" in reply_for("hi there")


def test_help_lists_capabilities():
    reply = reply_for("what can you do?")
    assert "reverse" in reply and "joke" in reply


def test_time():
    assert re.search(r"\d{2}:\d{2}", reply_for("what time is it"))


def test_date():
    assert "Today is" in reply_for("what's the date")


def test_reverse():
    assert "Reversed: dlrow olleh" in reply_for("reverse hello world")


def test_joke():
    reply = reply_for("tell me a joke")
    assert len(reply) > 10


def test_goodbye():
    assert "Goodbye" in reply_for("bye")


def test_empty_input_is_handled():
    assert "empty" in reply_for("   ")


def test_symbols_only_is_handled():
    assert "letters or numbers" in reply_for("@#$%^&*!!")


def test_too_long_input_is_handled():
    assert "too long" in reply_for("x" * 600)


def test_gibberish_falls_back_gracefully():
    assert "help" in reply_for("qwxzt plumbus florp").lower()
