import pandas as pd
from pathlib import Path

INPUT_FILE = Path("data/processed/trend_velocity.csv")
OUTPUT_FILE = Path("data/processed/trend_classified.csv")


def classify_trend(score, average_score):
    if score >= average_score * 2:
        return "EXPLODING"

    elif score >= average_score:
        return "GROWING"

    elif score >= average_score * 0.5:
        return "STABLE"

    else:
        return "WEAK"


def main():

    # Load velocity data
    df = pd.read_csv(INPUT_FILE)

    # Calculate average velocity
    average_score = df["velocity_score"].mean()

    # Classify each video
    df["trend_status"] = df["velocity_score"].apply(
        lambda score: classify_trend(
            score,
            average_score
        )
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
    print(f"Average velocity score: {average_score:.2f}")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nTrend Classification:\n")

    print(
        df[
            [
                "velocity_rank",
                "title",
                "velocity_score",
                "trend_status"
            ]
        ].head(10).to_string(index=False)
    )


if __name__ == "__main__":
    main()