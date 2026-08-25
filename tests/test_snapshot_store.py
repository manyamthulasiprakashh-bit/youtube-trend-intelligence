from src.ingestion.snapshot_store import (
    SNAPSHOT_COLUMNS,
    append_observations,
    data_readiness,
    load_snapshots,
)
from src.ingestion import collect_trending


def make_video(video_id="video-1", views="100"):
    return {
        "id": video_id,
        "snippet": {
            "publishedAt": "2026-08-23T00:00:00Z",
            "title": "Minecraft gameplay",
            "channelTitle": "Game Channel",
        },
        "statistics": {
            "viewCount": views,
            "likeCount": "10",
            "commentCount": "2",
        },
    }


def test_first_observation_is_stored_with_timestamp_and_metrics(tmp_path):
    snapshot_file = tmp_path / "snapshots.csv"

    assert append_observations(
        [make_video()], snapshot_file, collected_at="2026-08-24T00:00:00Z"
    ) == 1

    result = load_snapshots(snapshot_file)
    assert list(result.columns) == SNAPSHOT_COLUMNS
    assert result.loc[0, "video_id"] == "video-1"
    assert result.loc[0, "collected_at"] == "2026-08-24T00:00:00+00:00"
    assert result.loc[0, "views"] == 100
    assert result.loc[0, "category"] == "Gaming"
    assert result.loc[0, "velocity_score"] > 0


def test_repeated_observation_is_appended_without_overwriting_history(tmp_path):
    snapshot_file = tmp_path / "snapshots.csv"
    append_observations(
        [make_video(views="100")], snapshot_file, collected_at="2026-08-24T00:00:00Z"
    )
    append_observations(
        [make_video(views="250")], snapshot_file, collected_at="2026-08-25T00:00:00Z"
    )

    result = load_snapshots(snapshot_file)
    assert len(result) == 2
    assert result["video_id"].tolist() == ["video-1", "video-1"]
    assert result["views"].tolist() == [100, 250]
    assert result["collected_at"].nunique() == 2


def test_duplicate_collection_still_preserves_each_observation(tmp_path):
    snapshot_file = tmp_path / "snapshots.csv"
    video = make_video()

    append_observations([video], snapshot_file, collected_at="2026-08-24T00:00:00Z")
    append_observations([video], snapshot_file, collected_at="2026-08-24T00:00:00Z")

    assert len(load_snapshots(snapshot_file)) == 2


def test_data_readiness_statistics_and_24_hour_eligibility(tmp_path):
    snapshot_file = tmp_path / "snapshots.csv"
    append_observations(
        [make_video("video-1"), make_video("video-2")],
        snapshot_file,
        collected_at="2026-08-24T00:00:00Z",
    )
    append_observations(
        [make_video("video-1", views="200"), make_video("video-2", views="300")],
        snapshot_file,
        collected_at="2026-08-25T01:00:00Z",
    )
    append_observations(
        [make_video("video-3")],
        snapshot_file,
        collected_at="2026-08-25T01:00:00Z",
    )

    readiness = data_readiness(snapshot_file)
    assert readiness["unique_videos"] == 3
    assert readiness["observations"] == 5
    assert readiness["videos_with_repeated_observations"] == 2
    assert readiness["oldest_observation"] == "2026-08-24T00:00:00+00:00"
    assert readiness["newest_observation"] == "2026-08-25T01:00:00+00:00"
    assert readiness["sufficient_for_24h_training"] is True


def test_data_readiness_is_false_without_24_hour_repeated_history(tmp_path):
    snapshot_file = tmp_path / "snapshots.csv"
    append_observations(
        [make_video()], snapshot_file, collected_at="2026-08-24T00:00:00Z"
    )
    append_observations(
        [make_video(views="200")], snapshot_file, collected_at="2026-08-24T12:00:00Z"
    )

    assert data_readiness(snapshot_file)["sufficient_for_24h_training"] is False


def test_collection_command_appends_real_client_batch_and_reports_readiness(
    tmp_path, monkeypatch
):
    snapshot_file = tmp_path / "snapshots.csv"
    raw_file = tmp_path / "trending_videos.json"
    videos = [make_video("video-1"), make_video("video-2")]
    monkeypatch.setattr(collect_trending, "get_trending_videos", lambda **kwargs: videos)

    result = collect_trending.collect_and_store(
        max_results=2,
        raw_file=raw_file,
        snapshot_file=snapshot_file,
    )

    assert result["collected_count"] == 2
    assert result["stored_count"] == 2
    assert result["snapshot_file"] == str(snapshot_file)
    assert result["readiness"]["observations"] == 2
    assert len(load_snapshots(snapshot_file)) == 2
    assert raw_file.is_file()


def test_collection_command_repeated_runs_preserve_previous_observations(
    tmp_path, monkeypatch
):
    snapshot_file = tmp_path / "snapshots.csv"
    raw_file = tmp_path / "trending_videos.json"
    videos = [make_video("video-1")]
    monkeypatch.setattr(collect_trending, "get_trending_videos", lambda **kwargs: videos)

    collect_trending.collect_and_store(raw_file=raw_file, snapshot_file=snapshot_file)
    collect_trending.collect_and_store(raw_file=raw_file, snapshot_file=snapshot_file)

    result = load_snapshots(snapshot_file)
    assert len(result) == 2
    assert result["video_id"].tolist() == ["video-1", "video-1"]
    assert result["collected_at"].nunique() == 2


def test_collection_command_uses_one_timestamp_for_every_video_in_a_batch(
    tmp_path, monkeypatch
):
    snapshot_file = tmp_path / "snapshots.csv"
    raw_file = tmp_path / "trending_videos.json"
    videos = [make_video("video-1"), make_video("video-2")]
    monkeypatch.setattr(collect_trending, "get_trending_videos", lambda **kwargs: videos)

    collect_trending.collect_and_store(raw_file=raw_file, snapshot_file=snapshot_file)

    result = load_snapshots(snapshot_file)
    assert result["collected_at"].nunique() == 1