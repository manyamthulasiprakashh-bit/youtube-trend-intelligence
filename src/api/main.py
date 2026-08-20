from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from src.ai.gemini_analyzer import analyze_trend

app = FastAPI(
    title="YouTube Trend Intelligence API",
    description="API for YouTube trend analytics and AI insights",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "data/processed/trend_classified.csv"


@app.get("/")
def home():
    return {
        "message": "YouTube Trend Intelligence API",
        "status": "running",
    }


@app.get("/trends")
def get_trends():
    df = pd.read_csv(DATA_FILE)

    trends = df.head(20).to_dict(
        orient="records"
    )

    return {
        "count": len(trends),
        "trends": trends,
    }


@app.get("/trends/top")
def get_top_trends():
    df = pd.read_csv(DATA_FILE)

    top = df.head(10).to_dict(
        orient="records"
    )

    return {
        "count": len(top),
        "trends": top,
    }

@app.get("/trends/{video_id}/analysis")
def get_trend_analysis(video_id: str):

    df = pd.read_csv(DATA_FILE)

    video = df[df["video_id"] == video_id]

    if video.empty:
        return {
            "error": "Video not found"
        }

    video = video.iloc[0]

    analysis = analyze_trend(
        title=video["title"],
        channel=video["channel"],
        views=video["views"],
        likes=video["likes"],
        comments=video["comments"],
        velocity_score=video["velocity_score"],
    )

    return {
        "video_id": video_id,
        "title": video["title"],
        "analysis": analysis,
    }