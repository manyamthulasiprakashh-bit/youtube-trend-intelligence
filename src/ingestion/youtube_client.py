import os

from dotenv import load_dotenv
from googleapiclient.discovery import build


load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY is missing")


youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)


def get_trending_videos(
    region_code="IN",
    max_results=10
):
    request = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        chart="mostPopular",
        regionCode=region_code,
        maxResults=max_results
    )

    response = request.execute()

    return response["items"]