import pandas as pd
from pathlib import Path


INPUT_FILE = Path("data/processed/trending_videos.csv")
OUTPUT_FILE = Path("data/processed/clean_trending_videos.csv")


def main():
    df = pd.read_csv(INPUT_FILE)

    # Select useful columns
    df = df[
        [
            "id",
            "snippet.title",
            "snippet.channelTitle",
            "snippet.publishedAt",
            "statistics.viewCount",
            "statistics.likeCount",
            "statistics.commentCount",
        ]
    ]

    # Rename columns
    df = df.rename(
        columns={
            "id": "video_id",
            "snippet.title": "title",
            "snippet.channelTitle": "channel",
            "snippet.publishedAt": "published_at",
            "statistics.viewCount": "views",
            "statistics.likeCount": "likes",
            "statistics.commentCount": "comments",
        }
    )

    # Convert numbers
    df["views"] = pd.to_numeric(df["views"], errors="coerce").fillna(0)
    df["likes"] = pd.to_numeric(df["likes"], errors="coerce").fillna(0)
    df["comments"] = pd.to_numeric(df["comments"], errors="coerce").fillna(0)

    # Convert publication date
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")

    # Remove duplicate videos
    df = df.drop_duplicates(subset="video_id")

    # Save
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Cleaned {len(df)} videos")
    print(f"Saved to: {OUTPUT_FILE}")
    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))


if __name__ == "__main__":
    main()