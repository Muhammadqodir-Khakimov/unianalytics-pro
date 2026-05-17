"""Sentiment analysis — multilingual (uz/ru/en).

Production da multilingual BERT (HuggingFace transformers) ishlatiladi.
Hozir esa keyword-based fallback (HuggingFace o'rnatish 5GB+ memory).
"""
from typing import Any

# Oddiy keyword-based sentiment (production da BERT ishlatiladi)
POSITIVE_WORDS = {
    # uz
    "yaxshi", "ajoyib", "zo'r", "a'lo", "yutuq", "rahmat", "sevaman", "qiziq", "foydali", "tushunarli", "tinch", "yaxshi tushuntiradi", "mehribon", "professional",
    # ru
    "хорошо", "отлично", "прекрасно", "спасибо", "лучший", "интересно", "профессионал",
    # en
    "good", "great", "excellent", "amazing", "thanks", "best", "interesting", "professional", "helpful",
}

NEGATIVE_WORDS = {
    # uz
    "yomon", "qiyin", "tushunarsiz", "qattiq", "haqsiz", "kech", "bezovta", "rad etadi", "tushuntirmaydi", "qo'pol", "shafqatsiz",
    # ru
    "плохо", "ужасно", "трудно", "несправедливо", "грубый", "не понимаю",
    # en
    "bad", "terrible", "rude", "unfair", "difficult", "boring", "useless",
}

TOXIC_WORDS = {
    "ahmoq", "axmoq", "идиот", "stupid", "idiot",  # basic toxicity
}


def analyze_sentiment(text: str) -> dict[str, Any]:
    """Keyword-based sentiment analysis (production da BERT).

    Qaytaradi:
        label: positive/negative/neutral
        score: -1.0 dan 1.0 gacha
        toxicity: bool
    """
    if not text:
        return {"label": "neutral", "score": 0.0, "toxicity": False}

    text_lower = text.lower()
    words = set(text_lower.split())

    pos_count = sum(1 for w in POSITIVE_WORDS if w in text_lower)
    neg_count = sum(1 for w in NEGATIVE_WORDS if w in text_lower)
    toxic = any(t in text_lower for t in TOXIC_WORDS)

    total = pos_count + neg_count
    if total == 0:
        return {"label": "neutral", "score": 0.0, "toxicity": toxic}

    score = (pos_count - neg_count) / max(total, 1)
    label = "positive" if score > 0.2 else "negative" if score < -0.2 else "neutral"

    return {"label": label, "score": round(score, 3), "toxicity": toxic, "method": "keyword-based"}


def analyze_sentiment_bert(text: str) -> dict[str, Any]:
    """BERT sentiment (HuggingFace). Ishlatish uchun:
        pip install transformers torch

    Hozir disabled — keyword-based ishlatiladi.
    """
    try:
        from transformers import pipeline
        classifier = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
        result = classifier(text)[0]
        # Output: {'label': '4 stars', 'score': 0.85}
        stars = int(result["label"].split()[0])
        return {
            "label": "positive" if stars >= 4 else "negative" if stars <= 2 else "neutral",
            "score": (stars - 3) / 2,  # -1.0 ... +1.0
            "raw": result,
            "method": "bert",
        }
    except ImportError:
        return analyze_sentiment(text)


def generate_word_cloud_data(texts: list[str]) -> list[dict]:
    """Word cloud uchun ma'lumot."""
    from collections import Counter
    import re

    STOPWORDS = {"va", "yoki", "men", "siz", "u", "bu", "shu", "uchun", "bilan", "har", "ham", "bo'l", "I", "the", "and"}

    all_words = []
    for t in texts:
        words = re.findall(r"[a-zA-Zа-яА-ЯёЁ']+", t.lower())
        all_words.extend(w for w in words if len(w) > 2 and w not in STOPWORDS)

    counter = Counter(all_words)
    return [{"text": w, "value": c} for w, c in counter.most_common(50)]
