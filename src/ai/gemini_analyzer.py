from dotenv import load_dotenv
from google import genai
import os
import pandas as pd
import time


# Load environment variables
load_dotenv(".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing. Check your .env file."
    )


# Create Gemini client
client = genai.Client(api_key=api_key)


# Use a stable Gemini Flash model
MODEL_NAME = "gemini-3.6-flash"


def analyze_trend(
    title,
    channel,
    views,
    likes,
    comments,
    velocity_score,
):
    """
    Analyze a YouTube trend using Gemini.
    """

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

Give the analysis using exactly these sections:

1. Main Topic
Explain what the video is about based on the title and channel.

2. Why It Is Trending
Explain the possible reason for its high velocity and views.

3. Audience Signal
Analyze the relationship between views, likes and comments.

4. Trend Risk
Explain whether the trend appears sustainable or could decline quickly.

5. One-Sentence Summary
Give one concise sentence summarizing the trend.

IMPORTANT:
- Do not invent facts.
- Do not claim information that is not present in the data.
- Base the analysis on the provided metrics.
- Keep the answer concise and useful.
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

            return "Gemini returned an empty response."

        except Exception as error:

            print(
                f"Gemini request failed "
                f"(attempt {attempt + 1}/3): {error}"
            )

            # Retry after a short delay
            if attempt < 2:
                time.sleep(2)

    return (
        "AI analysis is temporarily unavailable. "
        "Please try again in a few seconds."
    )


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
        )

        print()
        print("🤖 AI ANALYSIS")
        print("-" * 70)
        print(result)

        print()
        print("=" * 70)


if __name__ == "__main__":
    main()