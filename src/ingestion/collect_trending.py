import json
from datetime import datetime, timezone
from pathlib import Path

try:
    from src.ingestion.snapshot_store import append_observations, data_readiness
    from src.ingestion.youtube_client import get_trending_videos
except ModuleNotFoundError:
    from snapshot_store import append_observations, data_readiness
    from youtube_client import get_trending_videos


DEFAULT_RAW_FILE = Path("data/raw/trending_videos.json")
DEFAULT_SNAPSHOT_FILE = Path("data/raw/trending_snapshots.csv")


def collect_and_store(
    region_code="IN",
    max_results=50,
    raw_file=DEFAULT_RAW_FILE,
    snapshot_file=DEFAULT_SNAPSHOT_FILE,
):
    """Collect one real batch and append it to the historical snapshot store."""
    videos = get_trending_videos(
        region_code=region_code,
        max_results=max_results,
    )
    collected_at = datetime.now(timezone.utc)

    raw_path = Path(raw_file)
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    with open(raw_path, "w", encoding="utf-8") as file:
        json.dump(videos, file, indent=2, ensure_ascii=False)

    stored_count = append_observations(
        videos,
        snapshot_file=snapshot_file,
        collected_at=collected_at,
    )
    readiness = data_readiness(snapshot_file)

    print(f"Collected {len(videos)} videos")
    print(f"Saved raw response to {raw_path}")
    print(f"Appended {stored_count} observations to {snapshot_file}")
    print(f"Dataset readiness: {readiness}")

    return {
        "collected_count": len(videos),
        "stored_count": stored_count,
        "raw_file": str(raw_path),
        "snapshot_file": str(snapshot_file),
        "readiness": readiness,
    }


def main():
    collect_and_store()


if __name__ == "__main__":
    main()