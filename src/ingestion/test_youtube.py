from youtube_client import get_trending_videos


videos = get_trending_videos(
    region_code="IN",
    max_results=10
)

for video in videos:
    print("=" * 60)
    print("Title:", video["snippet"]["title"])
    print("Channel:", video["snippet"]["channelTitle"])
    print("Video ID:", video["id"])
    print("Views:", video["statistics"].get("viewCount"))