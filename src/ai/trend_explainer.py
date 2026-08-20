import pandas as pd
from pathlib import Path


INPUT_FILE = Path(
    "data/processed/trend_classified.csv"
)


def explain_video(video):
    reasons = []

    # High velocity
    if video["views_per_hour"] > 100000:
        reasons.append(
            "The video is receiving views at a very high rate."
        )

    # Strong engagement
    if video["engagement_rate"] > 0.03:
        reasons.append(
            "The video has strong audience engagement."
        )

    # Large view count
    if video["views"] > 1_000_000:
        reasons.append(
            "The video has already attracted a large audience."
        )

    # Comments
    if video["comments"] > 1000:
        reasons.append(
            "The video is generating significant discussion."
        )

    # Fallback
    if not reasons:
        reasons.append(
            "The video is trending primarily because "
            "of its current momentum."
        )

    return reasons


def main():

    df = pd.read_csv(INPUT_FILE)

    # Analyze top 10 videos
    top_videos = df.head(10)

    print("\n" + "=" * 70)
    print("🤖 YOUTUBE TREND INTELLIGENCE REPORT")
    print("=" * 70)

    for _, video in top_videos.iterrows():

        print("\n🔥 TREND ALERT")
        print("-" * 70)

        print(f"Title: {video['title']}")
        print(f"Channel: {video['channel']}")
        print(f"Status: {video['trend_status']}")
        print(f"Views: {int(video['views']):,}")
        print(
            f"Views/hour: "
            f"{video['views_per_hour']:,.0f}"
        )
        print(
            f"Engagement rate: "
            f"{video['engagement_rate']:.2%}"
        )
        print(
            f"Velocity score: "
            f"{video['velocity_score']:,.2f}"
        )

        print("\nWhy is it trending?")

        reasons = explain_video(video)

        for number, reason in enumerate(
            reasons,
            start=1
        ):
            print(f"{number}. {reason}")


if __name__ == "__main__":
    main()