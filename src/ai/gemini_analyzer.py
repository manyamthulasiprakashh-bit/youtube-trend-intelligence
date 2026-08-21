from dotenv import load_dotenv
from google import genai
import os
import pandas as pd
import time


# Load environment variables
load_dotenv(".env")

api_key = os.getenv("GEMINI_API_KEY")

# Keep the API importable when Gemini is not configured. The analyzer returns
# the same safe failure response used for temporary provider failures.
client = genai.Client(api_key=api_key) if api_key else None


# Use a stable Gemini Flash model
MODEL_NAME = "gemini-3.6-flash"


def analyze_trend(
    title,
    channel,
    views,
    likes,
    comments,
    velocity_score,
    trend_strength=None,
    trend_status=None,
    category=None,
):
    """
    Analyze a YouTube trend using only the supplied metadata and metrics.
    """

    if client is None:
        return "AI analysis is temporarily unavailable."

    prompt = f"""
You are a YouTube Trend Intelligence Analyst.

Analyze the following YouTube trending video using ONLY the
information provided below.

Title: {title}
Channel: {channel}
Views: {views}
Likes: {likes}
Comments: {comments}
Velocity Score: {velocity_score}
Trend Strength: {trend_strength}
Trend Status: {trend_status}
Category: {category}

Give the analysis using exactly these seven sections and no others:

1. Main Topic
2. Why It Is Trending
3. Audience Signal
4. Trend Strength
5. Trend Risk
6. Future Outlook
7. One-Sentence Summary

Use the section heading exactly as written, followed by a concise answer.
For any conclusion not supported by the supplied data, write exactly:
"Insufficient data to determine."

IMPORTANT:
- Use only the supplied title, channel, category, status, and metrics.
- Do not invent facts or infer outside events, audience demographics, or causes.
- Keep every section concise and useful.
"""

    # Try the Gemini request
    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            if response.text:
                return response.text

            return "AI analysis is temporarily unavailable."

        except Exception as error:

            print(
                f"Gemini request failed "
                f"(attempt {attempt + 1}/3): {error}"
            )

            # Retry after a short delay
            if attempt < 2:
                time.sleep(2)

    return "AI analysis is temporarily unavailable."


def main():

    input_file = "data/processed/trend_velocity.csv"

    # Load trend data
    df = pd.read_csv(input_file)

    # Select top 10 fastest-growing videos
    top_videos = df.head(10)

    print()
    print("=" * 70)
    print("🤖 GEMINI YOUTUBE TREND INTELLIGENCE")
    print("=" * 70)

    for _, video in top_videos.iterrows():

        print()
        print("🔥 VIDEO")
        print("-" * 70)

        print("Rank:", video["velocity_rank"])
        print("Title:", video["title"])
        print("Channel:", video["channel"])
        print("Views:", video["views"])
        print("Likes:", video["likes"])
        print("Comments:", video["comments"])
        print("Velocity Score:", video["velocity_score"])

        result = analyze_trend(
            title=video["title"],
            channel=video["channel"],
            views=video["views"],
            likes=video["likes"],
            comments=video["comments"],
            velocity_score=video["velocity_score"],
            trend_strength=video.get("trend_strength"),
            trend_status=video.get("trend_status"),
            category=video.get("category"),
        )

        print()
        print("🤖 AI ANALYSIS")
        print("-" * 70)
        print(result)

        print()
        print("=" * 70)


if __name__ == "__main__":
    main()