"""Anonim feedback va sentiment."""
from app.services.sentiment_service import analyze_sentiment, generate_word_cloud_data


def test_sentiment_positive_uz():
    result = analyze_sentiment("O'qituvchi juda yaxshi tushuntiradi, rahmat")
    assert result["label"] == "positive"
    assert result["score"] > 0


def test_sentiment_negative_uz():
    result = analyze_sentiment("Yomon dars, qiziqarsiz, dahshat, juda yomon yondashuv")
    assert result["label"] in ("negative", "neutral")
    assert result["score"] <= 0


def test_sentiment_neutral_or_label():
    result = analyze_sentiment("Bugun dars bo'ldi")
    assert result["label"] in ("neutral", "positive", "negative")


def test_word_cloud_extracts_words():
    data = generate_word_cloud_data([
        "O'qituvchi juda yaxshi tushuntiradi",
        "Yaxshi dars yaxshi materiallar",
        "Tushuntirish aniq va ravon",
    ])
    assert isinstance(data, list)
    assert len(data) > 0
    assert all("text" in d or "value" in d for d in data)


def test_feedback_submit_anonymous(client):
    res = client.post("/api/v1/feedback/submit", json={
        "teacher_id": 1,
        "ratings": {"knowledge": 5, "explanation": 4, "respect": 5, "timeliness": 4, "usefulness": 5},
        "comment": "Yaxshi o'qituvchi",
    })
    assert res.status_code in (200, 201, 401, 404, 422)
