from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

try:
    from src.analytics.trend_classifier import classify_category
except ModuleNotFoundError:
    from trend_classifier import classify_category


DEFAULT_SNAPSHOT_FILE = Path("data/raw/trending_snapshots.csv")
MIN_REPEATED_VIDEOS_FOR_TRAINING = 2
MIN_OBSERVATION_SPAN_HOURS = 24

SNAPSHOT_COLUMNS = [
    "video_id",
    "collected_at",
    "views",
    "likes",
    "comments",
    "published_at",
    "title",
    "channel",
    "category",
    "age_hours",
    "views_per_hour",
    "engagement_rate",
    "velocity_score",
    "trend_score",
]


@dataclass(frozen=True)
class DataReadiness:
    unique_videos: int
    observations: int
    videos_with_repeated_observations: int
    oldest_observation: str | None
    newest_observation: str | None
    sufficient_for_24h_training: bool


def _utc_timestamp(value: datetime | pd.Timestamp | str | None = None) -> pd.Timestamp:
    timestamp = pd.Timestamp.now(tz="UTC") if value is None else pd.Timestamp(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("UTC")
    else:
        timestamp = timestamp.tz_convert("UTC")
    return timestamp


def _number(value: object) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def video_to_observation(
    video: dict,
    collected_at: datetime | pd.Timestamp | str | None = None,
) -> dict:
    """Normalize one YouTube API video into one immutable observation row."""
    snippet = video.get("snippet", {})
    statistics = video.get("statistics", {})
    collected_timestamp = _utc_timestamp(collected_at)
    published_timestamp = pd.to_datetime(
        snippet.get("publishedAt"),
        errors="coerce",
        utc=True,
    )
    age_hours = 0.0
    if not pd.isna(published_timestamp):
        age_hours = max(
            (collected_timestamp - published_timestamp).total_seconds() / 3600,
            1.0,
        )

    views = _number(statistics.get("viewCount"))
    likes = _number(statistics.get("likeCount"))
    comments = _number(statistics.get("commentCount"))
    engagement_rate = (likes + comments) / max(views, 1.0)
    views_per_hour = views / age_hours

    return {
        "video_id": str(video.get("id", "")),
        "collected_at": collected_timestamp.isoformat(),
        "views": views,
        "likes": likes,
        "comments": comments,
        "published_at": (
            published_timestamp.isoformat()
            if not pd.isna(published_timestamp)
            else ""
        ),
        "title": str(snippet.get("title", "")),
        "channel": str(snippet.get("channelTitle", "")),
        "category": classify_category(
            snippet.get("title", ""),
            snippet.get("channelTitle", ""),
        ),
        "age_hours": age_hours,
        "views_per_hour": views_per_hour,
        "engagement_rate": engagement_rate,
        "velocity_score": views_per_hour * (1 + engagement_rate),
        "trend_score": views * 0.60 + likes * 0.25 + comments * 0.15,
    }


def append_observations(
    videos: Iterable[dict],
    snapshot_file: Path | str = DEFAULT_SNAPSHOT_FILE,
    collected_at: datetime | pd.Timestamp | str | None = None,
) -> int:
    """Append API observations without replacing any existing history."""
    collection_timestamp = _utc_timestamp(collected_at)
    rows = [video_to_observation(video, collection_timestamp) for video in videos]
    if not rows:
        return 0

    path = Path(snapshot_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows, columns=SNAPSHOT_COLUMNS)
    frame.to_csv(path, mode="a", header=not path.exists(), index=False)
    return len(frame)


def load_snapshots(snapshot_file: Path | str = DEFAULT_SNAPSHOT_FILE) -> pd.DataFrame:
    """Load the append-only observation log, returning an empty schema if absent."""
    path = Path(snapshot_file)
    if not path.is_file():
        return pd.DataFrame(columns=SNAPSHOT_COLUMNS)
    return pd.read_csv(path)


def get_data_readiness(
    snapshot_file: Path | str = DEFAULT_SNAPSHOT_FILE,
    minimum_repeated_videos: int = MIN_REPEATED_VIDEOS_FOR_TRAINING,
    minimum_span_hours: float = MIN_OBSERVATION_SPAN_HOURS,
) -> DataReadiness:
    """Summarize whether snapshots can support 24-hour outcome labels."""
    frame = load_snapshots(snapshot_file)
    if frame.empty:
        return DataReadiness(0, 0, 0, None, None, False)

    collected = pd.to_datetime(frame["collected_at"], errors="coerce", utc=True)
    counts = frame.groupby("video_id").size()
    repeated = counts[counts > 1].index
    repeated_frame = frame[frame["video_id"].isin(repeated)].copy()
    repeated_times = pd.to_datetime(
        repeated_frame["collected_at"], errors="coerce", utc=True
    )
    repeated_frame["collected_timestamp"] = repeated_times
    grouped_timestamps = repeated_frame.groupby("video_id")["collected_timestamp"]
    span_by_video = (
        grouped_timestamps.max() - grouped_timestamps.min()
    ).dt.total_seconds() / 3600
    eligible_videos = int((span_by_video >= minimum_span_hours).sum())

    valid_collected = collected.dropna()
    oldest = valid_collected.min().isoformat() if not valid_collected.empty else None
    newest = valid_collected.max().isoformat() if not valid_collected.empty else None

    return DataReadiness(
        unique_videos=int(frame["video_id"].nunique()),
        observations=len(frame),
        videos_with_repeated_observations=len(repeated),
        oldest_observation=oldest,
        newest_observation=newest,
        sufficient_for_24h_training=eligible_videos >= minimum_repeated_videos,
    )


def data_readiness(
    snapshot_file: Path | str = DEFAULT_SNAPSHOT_FILE,
) -> dict:
    """Return data-readiness statistics as a JSON-serializable dictionary."""
    return asdict(get_data_readiness(snapshot_file))