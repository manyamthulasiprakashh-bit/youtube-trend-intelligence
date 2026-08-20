import pandas as pd
from pathlib import Path

INPUT_FILE = Path("data/processed/clean_trending_videos.csv")
OUTPUT_FILE = Path("data/processed/trend_velocity.csv")


def main():
    # Load cleaned YouTube data
    df = pd.read_csv(INPUT_FILE)

    # Convert columns to correct types
    df["views"] = pd.to_numeric(df["views"], errors="coerce").fillna(0)
    df["likes"] = pd.to_numeric(df["likes"], errors="coerce").fillna(0)
    df["comments"] = pd.to_numeric(df["comments"], errors="coerce").fillna(0)

    # Convert publication date
    df["published_at"] = pd.to_datetime(
        df["published_at"],
        errors="coerce",
        utc=True
    )

    # Current time
    now = pd.Timestamp.now(tz="UTC")

    # Calculate video age in hours
    df["age_hours"] = (
        (now - df["published_at"]).dt.total_seconds() / 3600
    )

    # Avoid division by zero
    df["age_hours"] = df["age_hours"].clip(lower=1)

    # Views gained per hour
    df["views_per_hour"] = (
        df["views"] / df["age_hours"]
    )

    # Engagement rate
    df["engagement_rate"] = (
        (df["likes"] + df["comments"]) / df["views"].clip(lower=1)
    )

    # Final velocity score
    df["velocity_score"] = (
        df["views_per_hour"] * (1 + df["engagement_rate"])
    )

    # Sort fastest-growing videos first
    result = df.sort_values(
        "velocity_score",
        ascending=False
    ).reset_index(drop=True)

    # Add ranking
    result["velocity_rank"] = range(1, len(result) + 1)

    # Select useful columns
    result = result[
        [
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
        ]
    ]

    # Save
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"Calculated velocity for {len(result)} videos")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nTop 10 Fastest Growing Videos:\n")

    print(
        result.head(10).to_string(index=False)
    )


if __name__ == "__main__":
    main()
