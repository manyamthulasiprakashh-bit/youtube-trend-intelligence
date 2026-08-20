import json
from pathlib import Path
import pandas as pd


INPUT_FILE = Path("data/raw/trending_videos.json")
OUTPUT_FILE = Path("data/processed/trending_videos.csv")


def main():
    # Load JSON data
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        videos = json.load(file)

    # Convert JSON to DataFrame
    df = pd.json_normalize(videos)

    # Save processed data
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Processed {len(df)} videos")
    print(f"Saved to: {OUTPUT_FILE}")
    print("\nColumns:")
    print(df.columns.tolist())


if __name__ == "__main__":
    main()