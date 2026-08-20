import json
from pathlib import Path

from youtube_client import get_trending_videos


def main():
    videos = get_trending_videos(
        region_code="IN",
        max_results=50
    )

    output_path = Path("data/raw/trending_videos.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(videos, file, indent=2, ensure_ascii=False)

    print(f"Saved {len(videos)} videos to {output_path}")


if __name__ == "__main__":
    main()