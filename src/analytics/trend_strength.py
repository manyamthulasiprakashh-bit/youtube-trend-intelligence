import pandas as pd


VELOCITY_WEIGHT = 0.50
ENGAGEMENT_WEIGHT = 0.30
REACH_WEIGHT = 0.20


def normalize_metric(value, maximum):
    """Normalize a non-negative metric against its dataset maximum."""
    if pd.isna(value) or pd.isna(maximum) or maximum <= 0:
        return 0.0

    return min(max(float(value) / float(maximum), 0.0), 1.0)


def calculate_trend_strength(
    velocity_score,
    engagement_rate,
    views,
    max_velocity_score,
    max_engagement_rate,
    max_views,
):
    """Return a 0-100 strength score from normalized reach signals."""
    # Velocity leads because it measures current momentum; engagement and
    # reach provide supporting audience and scale signals.
    normalized_velocity = normalize_metric(
        velocity_score,
        max_velocity_score,
    )
    normalized_engagement = normalize_metric(
        engagement_rate,
        max_engagement_rate,
    )
    normalized_reach = normalize_metric(views, max_views)

    strength = 100 * (
        VELOCITY_WEIGHT * normalized_velocity
        + ENGAGEMENT_WEIGHT * normalized_engagement
        + REACH_WEIGHT * normalized_reach
    )

    return round(min(max(strength, 0.0), 100.0), 2)


def add_trend_strength(df):
    """Add normalized trend strength to a velocity dataframe."""
    if df.empty:
        df["trend_strength"] = pd.Series(dtype=float)
        return df

    max_velocity_score = df["velocity_score"].max()
    max_engagement_rate = df["engagement_rate"].max()
    max_views = df["views"].max()

    df["trend_strength"] = df.apply(
        lambda row: calculate_trend_strength(
            velocity_score=row["velocity_score"],
            engagement_rate=row["engagement_rate"],
            views=row["views"],
            max_velocity_score=max_velocity_score,
            max_engagement_rate=max_engagement_rate,
            max_views=max_views,
        ),
        axis=1,
    )
    return df