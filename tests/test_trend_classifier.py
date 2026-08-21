import pandas as pd

from src.analytics.trend_classifier import classify_category, classify_trend
from src.analytics.trend_strength import calculate_trend_strength


def test_classify_category_uses_title_keywords():
    assert classify_category("Minecraft survival gameplay", "Creator") == "Gaming"
    assert classify_category("Official Audio - New Song", "Artist") == "Music"
    assert classify_category("iPhone review", "Tech Channel") == "Technology"


def test_classify_category_uses_channel_keywords():
    assert classify_category("Daily update", "World News") == "News"
    assert classify_category("New video", "Funny Comedy Club") == "Comedy"


def test_classify_category_falls_back_to_other():
    assert classify_category("A quiet day", "A channel") == "Other"


def test_trend_strength_uses_weighted_normalized_signals():
    assert calculate_trend_strength(50, 0.05, 500, 100, 0.10, 1000) == 50.0


def test_trend_strength_stays_in_range():
    assert calculate_trend_strength(500, 5, 5000, 100, 1, 1000) == 100.0
    assert calculate_trend_strength(-1, -1, -1, 100, 1, 1000) == 0.0


def test_trend_status_boundaries_and_each_level():
    assert classify_trend(80) == "EXPLODING"
    assert classify_trend(60) == "GROWING"
    assert classify_trend(40) == "STABLE"
    assert classify_trend(39.99) == "DECLINING"


def test_trend_status_thresholds_are_configurable():
    thresholds = {"EXPLODING": 90, "GROWING": 70, "STABLE": 50}
    assert classify_trend(89.99, thresholds) == "GROWING"
    assert classify_trend(50, thresholds) == "STABLE"


def test_classified_dataset_keeps_v1_fields_and_adds_category(tmp_path, monkeypatch):
    from src.analytics import trend_classifier

    input_file = tmp_path / "trend_velocity.csv"
    output_file = tmp_path / "trend_classified.csv"
    pd.DataFrame(
        [
            {
                "velocity_rank": 1,
                "video_id": "abc123",
                "title": "Football highlights",
                "channel": "Sports Channel",
                "views": 1000,
                "likes": 100,
                "comments": 10,
                "age_hours": 2,
                "views_per_hour": 500,
                "engagement_rate": 0.11,
                "velocity_score": 555,
            }
        ]
    ).to_csv(input_file, index=False)
    monkeypatch.setattr(trend_classifier, "INPUT_FILE", input_file)
    monkeypatch.setattr(trend_classifier, "OUTPUT_FILE", output_file)

    trend_classifier.main()

    result = pd.read_csv(output_file)
    assert result.loc[0, "category"] == "Sports"
    assert {
        "velocity_rank",
        "video_id",
        "title",
        "channel",
        "views",
        "likes",
        "comments",
        "age_hours",
        "views_per_hour",
        "engagement_rate",
        "velocity_score",
        "trend_status",
    }.issubset(result.columns)