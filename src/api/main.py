from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pydantic import BaseModel

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

V2_REQUIRED_COLUMNS = {
    "video_id",
    "title",
    "channel",
    "category",
    "views",
    "likes",
    "comments",
    "velocity_score",
    "trend_strength",
    "trend_status",
}


class CategoryCount(BaseModel):
    category: str
    count: int


class TrendSummary(BaseModel):
    total_videos: int
    top_categories: list[CategoryCount]
    average_trend_strength: float
    status_counts: dict[str, int]


class EmergingTrend(BaseModel):
    rank: int
    video_id: str
    title: str
    channel: str
    category: str
    views: float
    likes: float
    comments: float
    velocity_score: float
    trend_strength: float
    trend_status: str


def load_v2_data() -> pd.DataFrame:
    """Load and validate the classified dataset used by V2 read endpoints."""
    data_path = Path(DATA_FILE)
    if not data_path.is_file():
        raise HTTPException(status_code=500, detail="Processed trend data is unavailable")

    try:
        df = pd.read_csv(data_path)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
        raise HTTPException(
            status_code=500,
            detail="Processed trend data could not be read",
        ) from error

    missing_columns = V2_REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        raise HTTPException(
            status_code=500,
            detail="Processed trend data is missing required columns",
        )

    return df


def numeric_column(df: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(df[column], errors="coerce").fillna(0)


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


@app.get("/trends/summary", response_model=TrendSummary)
def get_trend_summary():
    df = load_v2_data()
    status_values = ("EXPLODING", "GROWING", "STABLE", "DECLINING")

    category_counts = (
        df["category"]
        .fillna("Other")
        .value_counts()
        .rename_axis("category")
        .reset_index(name="count")
        .sort_values(["count", "category"], ascending=[False, True])
    )

    return TrendSummary(
        total_videos=len(df),
        top_categories=[
            CategoryCount(category=row.category, count=int(row.count))
            for row in category_counts.itertuples()
        ],
        average_trend_strength=round(
            float(numeric_column(df, "trend_strength").mean())
            if not df.empty
            else 0.0,
            2,
        ),
        status_counts={
            status: int((df["trend_status"] == status).sum())
            for status in status_values
        },
    )


@app.get("/trends/emerging", response_model=list[EmergingTrend])
def get_emerging_trends():
    df = load_v2_data()
    if df.empty:
        return []

    ranked = df.copy()
    ranked["trend_strength"] = numeric_column(ranked, "trend_strength")
    ranked["velocity_score"] = numeric_column(ranked, "velocity_score")
    for column in ("views", "likes", "comments"):
        ranked[column] = numeric_column(ranked, column)
    ranked = ranked.sort_values(
        ["trend_strength", "velocity_score"],
        ascending=[False, False],
    ).head(10)

    emerging: list[EmergingTrend] = []
    for rank, row in enumerate(ranked.to_dict(orient="records"), start=1):
        emerging.append(
            EmergingTrend(
                rank=rank,
                video_id=str(row["video_id"]),
                title=str(row["title"]),
                channel=str(row["channel"]),
                category=str(row["category"]),
                views=float(row["views"]),
                likes=float(row["likes"]),
                comments=float(row["comments"]),
                velocity_score=float(row["velocity_score"]),
                trend_strength=float(row["trend_strength"]),
                trend_status=str(row["trend_status"]),
            )
        )

    return emerging

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
        trend_strength=video["trend_strength"],
        trend_status=video["trend_status"],
        category=video["category"],
    )

    return {
        "video_id": video_id,
        "title": video["title"],
        "analysis": analysis,
    }