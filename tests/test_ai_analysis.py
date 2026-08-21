from types import SimpleNamespace

from fastapi.testclient import TestClient

from src.ai import gemini_analyzer
from src.api import main


SECTION_HEADINGS = (
    "1. Main Topic",
    "2. Why It Is Trending",
    "3. Audience Signal",
    "4. Trend Strength",
    "5. Trend Risk",
    "6. Future Outlook",
    "7. One-Sentence Summary",
)


def test_analyze_trend_returns_the_required_sections(monkeypatch):
    prompt_seen = {}

    class FakeModels:
        def generate_content(self, model, contents):
            prompt_seen["model"] = model
            prompt_seen["contents"] = contents
            return SimpleNamespace(
                text="\n".join(f"{heading}\nSupported data." for heading in SECTION_HEADINGS)
            )

    monkeypatch.setattr(
        gemini_analyzer,
        "client",
        SimpleNamespace(models=FakeModels()),
    )

    result = gemini_analyzer.analyze_trend(
        title="Gaming showcase",
        channel="Game Channel",
        views=1000,
        likes=100,
        comments=10,
        velocity_score=500,
        trend_strength=75,
        trend_status="GROWING",
        category="Gaming",
    )

    assert all(heading in result for heading in SECTION_HEADINGS)
    assert prompt_seen["model"] == gemini_analyzer.MODEL_NAME
    assert "Trend Strength: 75" in prompt_seen["contents"]
    assert "Category: Gaming" in prompt_seen["contents"]


def test_analyze_trend_returns_safe_message_on_gemini_failure(monkeypatch):
    class FailingModels:
        def generate_content(self, model, contents):
            raise TimeoutError("provider timeout")

    monkeypatch.setattr(
        gemini_analyzer,
        "client",
        SimpleNamespace(models=FailingModels()),
    )
    monkeypatch.setattr(gemini_analyzer.time, "sleep", lambda seconds: None)

    result = gemini_analyzer.analyze_trend("Title", "Channel", 1, 1, 1, 1)

    assert result == "AI analysis is temporarily unavailable."


def test_analysis_endpoint_returns_structured_analysis(monkeypatch):
    expected = "\n".join(f"{heading}\nSupported data." for heading in SECTION_HEADINGS)
    captured = {}

    def fake_analyze_trend(**kwargs):
        captured.update(kwargs)
        return expected

    monkeypatch.setattr(main, "analyze_trend", fake_analyze_trend)
    response = TestClient(main.app).get("/trends/X1aFkAkFASk/analysis")

    assert response.status_code == 200
    payload = response.json()
    assert payload["video_id"] == "X1aFkAkFASk"
    assert payload["analysis"] == expected
    assert captured["category"] == "Movies & Entertainment"
    assert captured["trend_status"] == "EXPLODING"


def test_analysis_endpoint_returns_missing_video_error():
    response = TestClient(main.app).get("/trends/does-not-exist/analysis")

    assert response.status_code == 200
    assert response.json() == {"error": "Video not found"}