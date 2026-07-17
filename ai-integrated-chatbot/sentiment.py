"""Sentiment analysis backends for the AI-integrated chatbot.

Two implementations of the same tiny interface:

* AzureSentimentAnalyzer -- calls the Azure AI Language service
  (Text Analytics) using the official SDK. This is the real,
  cloud-based AI-as-a-service path.
* OfflineSentimentAnalyzer -- a small keyword-based stand-in used when
  no Azure credentials are configured, so the bot still runs locally
  (and so unit tests do not need network access).

Both return a dict:  {"label": "positive|neutral|negative|mixed",
                      "positive": float, "neutral": float, "negative": float}
"""


class SentimentUnavailable(Exception):
    """Raised when the sentiment backend cannot produce a result."""


class AzureSentimentAnalyzer:
    """Sentiment via Azure AI Language (Text Analytics) REST API."""

    def __init__(self, endpoint: str, key: str):
        # Imported here so the bot can run without the Azure SDK installed
        # when only the offline analyzer is used.
        from azure.ai.textanalytics import TextAnalyticsClient
        from azure.core.credentials import AzureKeyCredential

        self.client = TextAnalyticsClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

    def analyze(self, text: str) -> dict:
        try:
            docs = self.client.analyze_sentiment(documents=[text])
            result = docs[0]
            if result.is_error:
                raise SentimentUnavailable(str(result.error))
            return {
                "label": result.sentiment,
                "positive": result.confidence_scores.positive,
                "neutral": result.confidence_scores.neutral,
                "negative": result.confidence_scores.negative,
            }
        except SentimentUnavailable:
            raise
        except Exception as error:  # network, auth, quota, ...
            raise SentimentUnavailable(str(error)) from error


class OfflineSentimentAnalyzer:
    """Keyword-lexicon fallback used when Azure is not configured."""

    POSITIVE = {
        "love", "like", "great", "good", "awesome", "amazing", "happy",
        "excellent", "fantastic", "wonderful", "cool", "nice", "fun",
        "best", "enjoy", "thanks", "thank",
    }
    NEGATIVE = {
        "hate", "bad", "terrible", "awful", "sad", "angry", "horrible",
        "worst", "annoying", "broken", "frustrating", "frustrated",
        "useless", "boring", "stupid",
    }

    def analyze(self, text: str) -> dict:
        words = {w.strip(".,!?;:").lower() for w in text.split()}
        pos = len(words & self.POSITIVE)
        neg = len(words & self.NEGATIVE)
        total = max(pos + neg, 1)
        if pos and neg:
            label = "mixed"
        elif pos:
            label = "positive"
        elif neg:
            label = "negative"
        else:
            label = "neutral"
        return {
            "label": label,
            "positive": round(pos / total, 2) if pos else 0.0,
            "neutral": 1.0 if label == "neutral" else 0.0,
            "negative": round(neg / total, 2) if neg else 0.0,
        }


def build_analyzer(config):
    """Choose the Azure backend when configured, otherwise the offline one.

    Returns (analyzer, backend_name).
    """
    if config.API_KEY and config.ENDPOINT_URI:
        return (
            AzureSentimentAnalyzer(config.ENDPOINT_URI, config.API_KEY),
            "Azure AI Language",
        )
    return OfflineSentimentAnalyzer(), "offline lexicon (Azure not configured)"
