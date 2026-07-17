# SentiBot — Traditional Chatbot + Azure AI Language

MSAI-631-B02 · Artificial Intelligence for Human-Computer Interaction · University of the Cumberlands

## Origin of these files

This project is a copy of [`../traditional-chatbot`](../traditional-chatbot)
(the Prototype Simple Traditional Chatbot assignment), copied here so the
original rule-based bot stays intact as its own submission while this
version adds the AI-as-a-service integration required by the *Integrate
Traditional Chatbot with AI Service* assignment.

## What's new vs. the original

- `sentiment.py` — sentiment backends: **Azure AI Language** (Text
  Analytics SDK) plus an offline keyword fallback used when no Azure
  credentials are configured (also keeps unit tests network-free).
- `config.py` — extended `DefaultConfig` with `API_KEY` / `ENDPOINT_URI`
  read from environment variables (never hard-coded).
- `bot.py` — `RuleBasedBot` became `SentimentBot`: a new
  `sentiment <text>` command reports label + confidence scores, and the
  bot's tone adapts to the detected mood of every message.
- `app.py` — builds the analyzer at startup and injects it into the bot.

## Setup

```bash
conda create --name MSAI631_AI python=3.10
conda activate MSAI631_AI
cd ai-integrated-chatbot
pip install -r requirements.txt
```

Configure the Azure AI Language resource (Portal → your Language resource →
Keys and Endpoint):

```bash
# Windows
SET MicrosoftAPIKey=<key 1>
SET MicrosoftAIServiceEndpoint=https://<resource>.cognitiveservices.azure.com/

# macOS/Linux
export MicrosoftAPIKey=<key 1>
export MicrosoftAIServiceEndpoint=https://<resource>.cognitiveservices.azure.com/
```

Run:

```bash
python app.py
```

The startup log prints which sentiment backend is active. Connect the
[Bot Framework Emulator](https://github.com/microsoft/BotFramework-Emulator/releases)
to `http://localhost:3978/api/messages` (the `/api/messages` suffix is required).

## Try it

- `sentiment I love this class` → positive, with confidence scores
- `sentiment this is terrible and I am angry` → negative
- `help` → full capabilities list
- gibberish / `@#$%` / empty / 500+ chars → graceful error handling
- say something happy or frustrated and watch the bot's tone change

## Tests

```bash
python -m pytest test_bot.py -v
```

Tests use a fake analyzer (and the offline fallback), so they run without
Azure access.
