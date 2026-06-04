"""
analyzer.py
-----------
Pure-pandas analysis functions that work on the cleaned movie DataFrame
produced by `tmdb_client.fetch_top_rated_movies()`.

Each function returns a DataFrame / Series / scalar so the result can be
re-used by the CLI (`main.py`) and the Streamlit dashboard (`app.py`).
"""

import pandas as pd


# --------------------------------------------------------------------- #
def to_dataframe(movies: list[dict]) -> pd.DataFrame:
    """Convert the raw list of movie dictionaries into a pandas DataFrame."""
    df = pd.DataFrame(movies)
    if df.empty:
        return df

    df = df.reset_index(drop=True)
    df["rank"] = df.index + 1

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)
    df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0).astype(int)
    df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0)
    df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce").astype("Int64")
    return df


# --------------------------------------------------------------------- #
def calculate_golden_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the CineGold Golden Index Score for every movie.
    Formula: GoldenScore = (Rating * 50) + (Popularity * 0.3) + (VoteCount * 0.2)
    Adds a 'GoldenScore' column to the DataFrame.
    """
    df = df.copy()
    df["GoldenScore"] = (
        (df["rating"] * 50)
        + (df["popularity"] * 0.3)
        + (df["vote_count"] * 0.2)
    ).round(2)
    return df


def golden_leaderboard(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top-N movies sorted by GoldenScore."""
    if "GoldenScore" not in df.columns:
        df = calculate_golden_score(df)
    return df.sort_values("GoldenScore", ascending=False).head(n).reset_index(drop=True)


def hidden_gems(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Identify underrated movies:
    - Rating >= 8.0
    - Popularity below dataset average
    Returns top-N by GoldenScore.
    """
    if "GoldenScore" not in df.columns:
        df = calculate_golden_score(df)
    if df.empty:
        return df

    avg_popularity = df["popularity"].mean()
    gems = df[(df["rating"] >= 8.0) & (df["popularity"] < avg_popularity)]
    return gems.sort_values("GoldenScore", ascending=False).head(n).reset_index(drop=True)


# --------------------------------------------------------------------- #
def highest_rated(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top-N movies sorted by rating (ties broken by vote_count)."""
    return (
        df.sort_values(["rating", "vote_count"], ascending=[False, False])
        .head(n)
        .reset_index(drop=True)
    )


def most_popular(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top-N movies sorted by TMDb popularity."""
    return df.sort_values("popularity", ascending=False).head(n).reset_index(drop=True)


def top_by_votes(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top-N movies sorted by vote count (audience reach)."""
    return df.sort_values("vote_count", ascending=False).head(n).reset_index(drop=True)


def average_rating(df: pd.DataFrame) -> float:
    """Mean rating across the full dataset (rounded to 2 decimals)."""
    if df.empty:
        return 0.0
    return round(float(df["rating"].mean()), 2)


def movies_per_year(df: pd.DataFrame) -> pd.Series:
    """Count of movies grouped by release year (sorted by year)."""
    series = df.dropna(subset=["release_year"]).groupby("release_year").size()
    series.name = "count"
    return series.sort_index()


def rating_distribution(df: pd.DataFrame) -> pd.Series:
    """Frequency distribution of ratings binned to one decimal place."""
    return df["rating"].round(1).value_counts().sort_index()


def language_distribution(df: pd.DataFrame) -> pd.Series:
    """Number of movies for each original language."""
    return df["original_language"].value_counts()


def summary_stats(df: pd.DataFrame) -> dict:
    """High-level statistics displayed at the top of the dashboard / CLI."""
    if df.empty:
        return {}
    top = df.sort_values(["rating", "vote_count"], ascending=[False, False]).iloc[0]

    stats = {
        "total_movies": int(len(df)),
        "average_rating": average_rating(df),
        "highest_rating": float(df["rating"].max()),
        "lowest_rating": float(df["rating"].min()),
        "total_votes": int(df["vote_count"].sum()),
        "earliest_year": int(df["release_year"].min()) if df["release_year"].notna().any() else None,
        "latest_year": int(df["release_year"].max()) if df["release_year"].notna().any() else None,
        "languages": int(df["original_language"].nunique()),
        "top_movie": top["title"],
        "top_movie_rating": float(top["rating"]),
    }

    if "GoldenScore" in df.columns:
        gold_top = df.sort_values("GoldenScore", ascending=False).iloc[0]
        stats["highest_golden_score"] = float(df["GoldenScore"].max())
        stats["top_golden_movie"] = gold_top["title"]
        stats["top_golden_score_value"] = float(gold_top["GoldenScore"])

    return stats


# --------------------------------------------------------------------- #
def filter_by_year(df: pd.DataFrame, start: int | None = None, end: int | None = None) -> pd.DataFrame:
    """Return movies released between `start` and `end` (inclusive)."""
    out = df.copy()
    if start is not None:
        out = out[out["release_year"].fillna(0).astype(int) >= start]
    if end is not None:
        out = out[out["release_year"].fillna(9999).astype(int) <= end]
    return out.reset_index(drop=True)


def filter_by_catalog(df: pd.DataFrame, catalog: str | None) -> pd.DataFrame:
    """Filter by catalog label (Global Top Rated, Tamil Cinema, Global & Tamil, or All)."""
    if not catalog or catalog == "All":
        return df
    if "catalog" not in df.columns:
        return df
    if catalog == "Tamil Cinema":
        mask = df["catalog"].isin(["Tamil Cinema", "Global & Tamil"])
    elif catalog == "Global Top Rated":
        mask = df["catalog"].isin(["Global Top Rated", "Global & Tamil"])
    else:
        mask = df["catalog"] == catalog
    return df[mask].reset_index(drop=True)


def sort_movies(df: pd.DataFrame, by: str = "rating", ascending: bool = False) -> pd.DataFrame:
    """Sort movies by a chosen column."""
    if by not in df.columns:
        return df
    return df.sort_values(by, ascending=ascending).reset_index(drop=True)
