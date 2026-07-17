# TradBot — Simple Traditional (Rule-Based) Chatbot

MSAI-631-B02 · Artificial Intelligence for Human-Computer Interaction · University of the Cumberlands

A simple chatbot built with the **Microsoft Bot Framework** (Python) using a
**traditional, rule-based approach** — deterministic regex pattern matching,
no machine learning or LLMs.

## Capabilities

- Greets users and introduces itself
- `help` — lists all its capabilities
- Tells the current **time** and **date**
- `reverse <text>` — reverses any text
- Tells **jokes**
- Answers "who are you"
- Says goodbye
- Gracefully handles malformed input: empty messages, symbol-only text,
  over-long messages (>500 chars), and unrecognized phrases

## Architecture

```
Bot Framework Emulator ──HTTP POST /api/messages──▶ app.py (aiohttp + BotFrameworkAdapter)
                                                        │
                                                        ▼
                                              bot.py (RuleBasedBot)
                                        validate() → interpret() → respond()
```

The NLU layer is isolated in `RuleBasedBot.interpret()`, so the regex rule
engine can later be replaced by an AI-as-a-service offering (e.g., Azure
Cognitive Services CLU/LUIS) without changing the server plumbing.

## Setup

```bash
conda create --name MSAI631_MBF python=3.10
conda activate MSAI631_MBF
cd traditional-chatbot
pip install -r requirements.txt
python app.py
```

The bot listens on `http://localhost:3978/api/messages`.

## Testing

1. Install the [Bot Framework Emulator](https://github.com/microsoft/BotFramework-Emulator/releases)
2. Open Bot → `http://localhost:3978/api/messages` (the `/api/messages` suffix is required) → Connect
3. Chat!

Unit tests (no emulator needed):

```bash
python -m pytest test_bot.py -v
```
