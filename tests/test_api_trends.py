import pandas as pd
from fastapi.testclient import TestClient

from src.api import main


def make_dataset(path, rows):
    pd.DataFrame(rows).to_csv(path, index=False)


def test_summary_endpoint_returns_calculated_values(tmp_path, monkeypatch):
    data_file = tmp_path / "trend_classified.csv"
    make_dataset(
        data_file,
        [
            {
                "video_id": "one",
                "title": "Gaming video",
                "channel": "Channel A",
                "category": "Gaming",
                "views": 100,
                "likes": 10,
                "comments": 2,
                "velocity_score": 50,
                "trend_strength": 80,
                "trend_status": "EXPLODING",
            },
            {
                "video_id": "two",
                "title": "Music video",
                "channel": "Channel B",
                "category": "Music",
                "views": 200,
                "likes": 20,
                "comments": 4,
                "velocity_score": 25,
                "trend_strength": 40,
                "trend_status": "STABLE",
            },
        ],
    )
    monkeypatch.setattr(main, "DATA_FILE", str(data_file))

    response = TestClient(main.app).get("/trends/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_videos": 2,
        "top_categories": [
            {"category": "Gaming", "count": 1},
            {"category": "Music", "count": 1},
        ],
        "average_trend_strength": 60.0,
        "status_counts": {
            "EXPLODING": 1,
            "GROWING": 0,
            "STABLE": 1,
            "DECLINING": 0,
        },
    }


def test_emerging_endpoint_ranks_by_strength_then_velocity(tmp_path, monkeypatch):
    data_file = tmp_path / "trend_classified.csv"
    make_dataset(
        data_file,
        [
            {
                "video_id": "slow",
                "title": "Lower strength",
                "channel": "Channel",
                "category": "Other",
                "views": 1,
                "likes": 2,
                "comments": 3,
                "velocity_score": 90,
                "trend_strength": 50,
                "trend_status": "STABLE",
            },
            {
                "video_id": "fast",
                "title": "Highest strength",
                "channel": "Channel",
                "category": "Technology",
                "views": 4,
                "likes": 5,
                "comments": 6,
                "velocity_score": 100,
                "trend_strength": 90,
                "trend_status": "EXPLODING",
            },
        ],
    )
    monkeypatch.setattr(main, "DATA_FILE", str(data_file))

    response = TestClient(main.app).get("/trends/emerging")

    assert response.status_code == 200
    assert response.json()[0] == {
        "rank": 1,
        "video_id": "fast",
        "title": "Highest strength",
        "channel": "Channel",
        "category": "Technology",
        "views": 4.0,
        "likes": 5.0,
        "comments": 6.0,
        "velocity_score": 100.0,
        "trend_strength": 90.0,
        "trend_status": "EXPLODING",
    }


def test_summary_and_emerging_handle_empty_dataset(tmp_path, monkeypatch):
    data_file = tmp_path / "trend_classified.csv"
    pd.DataFrame(columns=sorted(main.V2_REQUIRED_COLUMNS)).to_csv(
        data_file,
        index=False,
    )
    monkeypatch.setattr(main, "DATA_FILE", str(data_file))
    client = TestClient(main.app)

    summary = client.get("/trends/summary")
    emerging = client.get("/trends/emerging")

    assert summary.status_code == 200
    assert summary.json() == {
        "total_videos": 0,
        "top_categories": [],
        "average_trend_strength": 0.0,
        "status_counts": {
            "EXPLODING": 0,
            "GROWING": 0,
            "STABLE": 0,
            "DECLINING": 0,
        },
    }
    assert emerging.status_code == 200
    assert emerging.json() == []


def test_v2_endpoints_return_500_when_dataset_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DATA_FILE", str(tmp_path / "missing.csv"))
    client = TestClient(main.app)

    assert client.get("/trends/summary").status_code == 500
    assert client.get("/trends/emerging").status_code == 500