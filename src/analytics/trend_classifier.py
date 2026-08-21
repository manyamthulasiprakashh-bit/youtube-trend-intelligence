import pandas as pd
from pathlib import Path

try:
    from src.analytics.trend_strength import add_trend_strength
except ModuleNotFoundError:
    from trend_strength import add_trend_strength

INPUT_FILE = Path("data/processed/trend_velocity.csv")
OUTPUT_FILE = Path("data/processed/trend_classified.csv")

STATUS_THRESHOLDS = {
    "EXPLODING": 80.0,
    "GROWING": 60.0,
    "STABLE": 40.0,
}

CATEGORY_KEYWORDS = {
    "Gaming": (
        "gaming", "gameplay", "minecraft", "fortnite", "roblox", "gta",
        "playstation", "ps5", "xbox", "esports"
    ),
    "Music": (
        "music", "song", "official audio", "lyrics", "concert", "album",
        "remix", "singer", "sings"
    ),
    "Movies & Entertainment": (
        "movie", "film", "trailer", "marvel", "dc", "netflix", "disney",
        "series", "anime", "actor", "entertainment"
    ),
    "Technology": (
        "technology", "tech", "iphone", "android", "google", "software",
        "gadget", "laptop", "smartphone", "artificial intelligence", " ai "
    ),
    "Education": (
        "education", "educational", "tutorial", "lesson", "course", "study",
        "exam", "learn", "science", "history"
    ),
    "Sports": (
        "sports", "football", "soccer", "cricket", "basketball", "tennis",
        "olympics", "fifa", "league", "match", "highlights"
    ),
    "News": (
        "news", "breaking", "update", "election", "politics", "report",
        "latest", "headline"
    ),
    "Lifestyle": (
        "lifestyle", "travel", "vlog", "fashion", "beauty", "fitness",
        "recipe", "cooking", "home"
    ),
    "Comedy": (
        "comedy", "comedian", "funny", "standup", "stand-up", "roast",
        "prank", "humor"
    ),
}


def classify_category(title, channel):
    """Classify a video using explicit keywords from its title and channel."""
    text = f"{title or ''} {channel or ''}".lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category

    return "Other"


def classify_trend(strength, thresholds=STATUS_THRESHOLDS):
    """Classify strength using configurable inclusive lower boundaries."""
    if strength >= thresholds["EXPLODING"]:
        return "EXPLODING"

    elif strength >= thresholds["GROWING"]:
        return "GROWING"

    elif strength >= thresholds["STABLE"]:
        return "STABLE"

    else:
        return "DECLINING"


def main():

    # Load velocity data
    df = pd.read_csv(INPUT_FILE)

    df = add_trend_strength(df)

    # Classify each video
    df["trend_status"] = df["trend_strength"].apply(
        classify_trend
    )

    df["category"] = df.apply(
        lambda row: classify_category(row["title"], row["channel"]),
        axis=1
    )

    # Sort by velocity
    df = df.sort_values(
        "velocity_score",
        ascending=False
    )

    # Save
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"Classified {len(df)} videos")
    print(f"Average trend strength: {df['trend_strength'].mean():.2f}")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nTrend Classification:\n")

    print(
        df[
            [
                "velocity_rank",
                "title",
                "velocity_score",
                "trend_strength",
                "trend_status",
                "category"
            ]
        ].head(10).to_string(index=False)
    )


if __name__ == "__main__":
    main()