import pandas as pd
from pathlib import Path


INPUT_FILE = Path("data/processed/clean_trending_videos.csv")
OUTPUT_FILE = Path("data/processed/trending_scores.csv")


def main():
    df = pd.read_csv(INPUT_FILE)

    # Make sure numeric columns are numbers
    df["views"] = pd.to_numeric(df["views"], errors="coerce").fillna(0)
    df["likes"] = pd.to_numeric(df["likes"], errors="coerce").fillna(0)
    df["comments"] = pd.to_numeric(df["comments"], errors="coerce").fillna(0)

    # Engagement rate
    df["engagement_rate"] = (
        (df["likes"] + df["comments"]) / df["views"].replace(0, 1)
    )

    # Simple trend score
    df["trend_score"] = (
        df["views"] * 0.6
        + df["likes"] * 0.25
        + df["comments"] * 0.15
    )

    # Rank videos
    df["trend_rank"] = (
        df["trend_score"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )

    # Sort by trend score
    df = df.sort_values("trend_score", ascending=False)

    # Save
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Calculated trend scores for {len(df)} videos")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nTop 10 Trending Videos:")
    print(
        df[
            [
                "trend_rank",
                "title",
                "channel",
                "views",
                "likes",
                "comments",
                "engagement_rate",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()