"""
visualizer.py
-------------
Generates charts (PNG bytes or file paths) from the movies DataFrame.

Charts produced:
  1. Top 10 rated movies
  2. Rating distribution histogram
  3. Movies released per year
  4. Popularity comparison
  5. GoldenScore Top 10 Bar Chart (NEW)
  6. Hidden Gems Chart (NEW)
  7. GoldenScore Distribution Chart (NEW)
"""

import io
import os
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from analyzer import (
    highest_rated,
    most_popular,
    movies_per_year,
    rating_distribution,
    golden_leaderboard,
    hidden_gems,
    calculate_golden_score,
)

GOLD = "#C9A227"
GOLD_DARK = "#8B6914"
GOLD_LIGHT = "#E8D5A3"
CHARCOAL = "#1a1a1a"
CREAM = "#FDF8F0"
GEM_COLOR = "#4A90D9"
GEM_LIGHT = "#A8C8F0"

sns.set_theme(style="whitegrid", palette=[GOLD, GOLD_DARK, GOLD_LIGHT, "#B8860B", "#D4AF37"])
plt.rcParams.update({
    "figure.dpi": 110,
    "savefig.dpi": 130,
    "figure.facecolor": CREAM,
    "axes.facecolor": "#FFFCF5",
    "axes.titleweight": "bold",
    "axes.titlesize": 14,
    "axes.titlecolor": CHARCOAL,
    "axes.labelcolor": CHARCOAL,
    "axes.labelsize": 11,
    "text.color": CHARCOAL,
    "xtick.color": CHARCOAL,
    "ytick.color": CHARCOAL,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": GOLD_DARK,
    "grid.color": GOLD_LIGHT,
    "grid.alpha": 0.45,
})


def _ensure_dir(folder: str) -> None:
    os.makedirs(folder, exist_ok=True)


def _fig_to_bytes(fig) -> bytes:
    """Convert a matplotlib figure to PNG bytes for Streamlit display."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


# --------------------------------------------------------------------- #
def plot_top_rated(df: pd.DataFrame, folder: str = "charts") -> bytes:
    """Horizontal bar chart of the 10 highest-rated movies."""
    _ensure_dir(folder)
    top10 = highest_rated(df, 10)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=top10, x="rating", y="title", hue="title",
        palette=[GOLD, GOLD_DARK, "#D4AF37", "#B8860B", GOLD_LIGHT] * 2,
        ax=ax, legend=False,
    )
    ax.set_title("Top 10 Highest-Rated Movies")
    ax.set_xlabel("Rating")
    ax.set_ylabel("")
    ax.set_xlim(top10["rating"].min() - 0.2, 10)

    for i, value in enumerate(top10["rating"]):
        ax.text(value + 0.02, i, f"{value:.2f}", va="center", fontsize=10, color=CHARCOAL)

    fig.tight_layout()
    path = os.path.join(folder, "top_10_rated.png")
    fig.savefig(path)
    return _fig_to_bytes(plt.figure())


def plot_top_rated_bytes(df: pd.DataFrame) -> bytes:
    top10 = highest_rated(df, 10)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=top10, x="rating", y="title", hue="title",
        palette=[GOLD, GOLD_DARK, "#D4AF37", "#B8860B", GOLD_LIGHT] * 2,
        ax=ax, legend=False,
    )
    ax.set_title("Top 10 Highest-Rated Movies")
    ax.set_xlabel("Rating")
    ax.set_ylabel("")
    if not top10.empty:
        ax.set_xlim(top10["rating"].min() - 0.2, 10)
    for i, value in enumerate(top10["rating"]):
        ax.text(value + 0.02, i, f"{value:.2f}", va="center", fontsize=10, color=CHARCOAL)
    fig.tight_layout()
    return _fig_to_bytes(fig)


def plot_rating_distribution(df: pd.DataFrame, folder: str = "charts") -> bytes:
    _ensure_dir(folder)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df["rating"], bins=20, kde=True, color=GOLD, edgecolor=GOLD_LIGHT, ax=ax)
    ax.set_title("Rating Distribution")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Number of Movies")
    fig.tight_layout()
    path = os.path.join(folder, "rating_distribution.png")
    fig.savefig(path)
    return _fig_to_bytes(plt.figure())


def plot_rating_distribution_bytes(df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df["rating"], bins=20, kde=True, color=GOLD, edgecolor=GOLD_LIGHT, ax=ax)
    ax.set_title("Rating Distribution")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Number of Movies")
    fig.tight_layout()
    return _fig_to_bytes(fig)


def plot_movies_per_year(df: pd.DataFrame, folder: str = "charts") -> bytes:
    _ensure_dir(folder)
    counts = movies_per_year(df)
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.fill_between(counts.index, counts.values, alpha=0.28, color=GOLD_LIGHT)
    ax.plot(counts.index, counts.values, marker="o", linewidth=2, color=GOLD_DARK, markerfacecolor=GOLD)
    ax.set_title("Top-Rated Movies by Release Year")
    ax.set_xlabel("Release Year")
    ax.set_ylabel("Number of Movies")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(folder, "movies_per_year.png")
    fig.savefig(path)
    return _fig_to_bytes(plt.figure())


def plot_movies_per_year_bytes(df: pd.DataFrame) -> bytes:
    counts = movies_per_year(df)
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.fill_between(counts.index, counts.values, alpha=0.28, color=GOLD_LIGHT)
    ax.plot(counts.index, counts.values, marker="o", linewidth=2, color=GOLD_DARK, markerfacecolor=GOLD)
    ax.set_title("Top-Rated Movies by Release Year")
    ax.set_xlabel("Release Year")
    ax.set_ylabel("Number of Movies")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return _fig_to_bytes(fig)


def plot_popularity(df: pd.DataFrame, folder: str = "charts") -> bytes:
    _ensure_dir(folder)
    top10 = most_popular(df, 10)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=top10, x="popularity", y="title", hue="title",
        palette=[GOLD_DARK, GOLD, "#D4AF37", "#B8860B", GOLD_LIGHT] * 2,
        ax=ax, legend=False,
    )
    ax.set_title("Top 10 Most Popular Movies")
    ax.set_xlabel("Popularity Score")
    ax.set_ylabel("")
    for i, value in enumerate(top10["popularity"]):
        ax.text(value + 0.5, i, f"{value:.1f}", va="center", fontsize=10, color=CHARCOAL)
    fig.tight_layout()
    path = os.path.join(folder, "popularity_top10.png")
    fig.savefig(path)
    return _fig_to_bytes(plt.figure())


def plot_popularity_bytes(df: pd.DataFrame) -> bytes:
    top10 = most_popular(df, 10)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=top10, x="popularity", y="title", hue="title",
        palette=[GOLD_DARK, GOLD, "#D4AF37", "#B8860B", GOLD_LIGHT] * 2,
        ax=ax, legend=False,
    )
    ax.set_title("Top 10 Most Popular Movies")
    ax.set_xlabel("Popularity Score")
    ax.set_ylabel("")
    for i, value in enumerate(top10["popularity"]):
        ax.text(value + 0.5, i, f"{value:.1f}", va="center", fontsize=10, color=CHARCOAL)
    fig.tight_layout()
    return _fig_to_bytes(fig)


# ---- NEW CHARTS ---- #

def plot_golden_score_top10(df: pd.DataFrame) -> bytes:
    """Horizontal bar chart of the Top 10 movies by GoldenScore."""
    if "GoldenScore" not in df.columns:
        df = calculate_golden_score(df)

    top10 = golden_leaderboard(df, 10)
    if top10.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No data available", ha="center", va="center")
        return _fig_to_bytes(fig)

    fig, ax = plt.subplots(figsize=(12, 7))
    colors = [GOLD, GOLD_DARK, "#D4AF37", "#B8860B", GOLD_LIGHT] * 2
    bars = ax.barh(range(len(top10)), top10["GoldenScore"], color=colors[:len(top10)])

    ax.set_yticks(range(len(top10)))
    ax.set_yticklabels(top10["title"], fontsize=10)
    ax.invert_yaxis()
    ax.set_title("GoldenScore Top 10 Leaderboard", fontsize=15, pad=15)
    ax.set_xlabel("Golden Index Score")

    for i, (bar, value) in enumerate(zip(bars, top10["GoldenScore"])):
        ax.text(
            bar.get_width() + top10["GoldenScore"].max() * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{value:,.1f}", va="center", fontsize=9, color=CHARCOAL, fontweight="bold",
        )

    fig.tight_layout()
    return _fig_to_bytes(fig)


def plot_hidden_gems(df: pd.DataFrame) -> bytes:
    """Scatter/bar chart showing Hidden Gems (high rating, low popularity)."""
    if "GoldenScore" not in df.columns:
        df = calculate_golden_score(df)

    gems = hidden_gems(df, 10)
    if gems.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No hidden gems found in current filter", ha="center", va="center")
        return _fig_to_bytes(fig)

    fig, ax = plt.subplots(figsize=(12, 7))
    scatter = ax.scatter(
        gems["popularity"], gems["rating"],
        s=gems["GoldenScore"] / gems["GoldenScore"].max() * 400 + 80,
        c=gems["GoldenScore"], cmap="YlOrBr",
        alpha=0.85, edgecolors=GOLD_DARK, linewidths=1.2, zorder=3,
    )
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("GoldenScore", color=CHARCOAL)

    for _, row in gems.iterrows():
        ax.annotate(
            row["title"][:20] + ("…" if len(row["title"]) > 20 else ""),
            (row["popularity"], row["rating"]),
            textcoords="offset points", xytext=(6, 4),
            fontsize=8, color=CHARCOAL,
        )

    avg_pop = df["popularity"].mean()
    ax.axvline(avg_pop, color=GOLD, linestyle="--", alpha=0.6, label=f"Avg Popularity ({avg_pop:.1f})")
    ax.legend(fontsize=9)

    ax.set_title("Hidden Gems — High Rating, Low Popularity", fontsize=15, pad=15)
    ax.set_xlabel("Popularity")
    ax.set_ylabel("Rating")
    fig.tight_layout()
    return _fig_to_bytes(fig)


def plot_golden_distribution(df: pd.DataFrame) -> bytes:
    """Distribution histogram of GoldenScore across all filtered movies."""
    if "GoldenScore" not in df.columns:
        df = calculate_golden_score(df)

    if df.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No data available", ha="center", va="center")
        return _fig_to_bytes(fig)

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.histplot(df["GoldenScore"], bins=25, kde=True, color=GOLD, edgecolor=GOLD_DARK, ax=ax)

    mean_score = df["GoldenScore"].mean()
    ax.axvline(mean_score, color=GOLD_DARK, linestyle="--", linewidth=1.8,
               label=f"Mean GoldenScore: {mean_score:,.1f}")
    ax.legend(fontsize=10)

    ax.set_title("GoldenScore Distribution", fontsize=15, pad=15)
    ax.set_xlabel("Golden Index Score")
    ax.set_ylabel("Number of Movies")
    fig.tight_layout()
    return _fig_to_bytes(fig)


# --------------------------------------------------------------------- #
def generate_all_charts(df: pd.DataFrame, folder: str = "charts") -> list[str]:
    """Convenience wrapper that produces every chart and returns their paths."""
    _ensure_dir(folder)

    if "GoldenScore" not in df.columns:
        from analyzer import calculate_golden_score
        df = calculate_golden_score(df)

    paths = []
    chart_funcs = [
        ("top_10_rated.png", plot_top_rated_bytes),
        ("rating_distribution.png", plot_rating_distribution_bytes),
        ("movies_per_year.png", plot_movies_per_year_bytes),
        ("popularity_top10.png", plot_popularity_bytes),
        ("golden_score_top10.png", plot_golden_score_top10),
        ("hidden_gems.png", plot_hidden_gems),
        ("golden_distribution.png", plot_golden_distribution),
    ]

    for filename, func in chart_funcs:
        path = os.path.join(folder, filename)
        img_bytes = func(df)
        with open(path, "wb") as f:
            f.write(img_bytes)
        paths.append(path)

    return paths
