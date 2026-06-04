"""
main.py
-------
Command-line entry point for the CineGold Movie Rating Analyzer.

Run with:
    python main.py
    python main.py --no-menu
"""

import os
import sys
from pathlib import Path

from tabulate import tabulate
import pandas as pd

from dotenv import load_dotenv
from tmdb_client import fetch_top_rated_movies
from analyzer import (
    to_dataframe, highest_rated, most_popular, top_by_votes,
    summary_stats, filter_by_year, sort_movies,
    calculate_golden_score, golden_leaderboard, hidden_gems,
)
from exporter import export_to_csv, export_filtered_csv, export_pdf
from visualizer import generate_all_charts
from search import search_by_title


def print_header(text: str) -> None:
    line = "=" * 60
    print(f"\n{line}\n{text.center(60)}\n{line}")


def print_table(df: pd.DataFrame, cols: list[str] | None = None) -> None:
    if df.empty:
        print("  (no rows)\n")
        return
    cols = cols or ["rank", "title", "release_year", "rating", "popularity"]
    cols = [c for c in cols if c in df.columns]
    print(tabulate(df[cols], headers="keys", tablefmt="fancy_grid",
                   showindex=False, floatfmt=".2f"))


def run_analysis() -> pd.DataFrame:
    load_dotenv(Path(__file__).resolve().parent / ".env")
    total = int(os.environ.get("TOTAL_MOVIES", "250"))

    print_header("CineGold Movie Rating Analyzer (TMDb edition)")
    print(f"Target: top {total} movies from TMDb\n")

    try:
        movies = fetch_top_rated_movies(total_movies=total)
    except RuntimeError as err:
        print(f"\nERROR: {err}")
        sys.exit(1)

    if not movies:
        print("ERROR: API returned no movies. Check your internet / API key.")
        sys.exit(1)

    df = to_dataframe(movies)
    df = calculate_golden_score(df)

    csv_path = export_to_csv(df, "movies.csv")
    print(f"\nCSV exported  ->  {csv_path}")

    print("Generating charts ...")
    chart_paths = generate_all_charts(df, folder="charts")
    for p in chart_paths:
        print(f"   + {p}")

    print("Auto-saving filtered reports to exports/ ...")
    try:
        _, filtered_csv = export_filtered_csv(df)
        print(f"   + {filtered_csv}")
        _, pdf_path = export_pdf(df, stats=summary_stats(df))
        print(f"   + {pdf_path}")
    except Exception as e:
        print(f"   (export skipped: {e})")

    stats = summary_stats(df)
    print_header("Summary Statistics")
    print(f"  Total movies fetched : {stats['total_movies']}")
    print(f"  Average rating       : {stats['average_rating']}")
    print(f"  Highest rating       : {stats['highest_rating']:.2f}")
    print(f"  Lowest rating        : {stats['lowest_rating']:.2f}")
    print(f"  Total votes          : {stats['total_votes']:,}")
    print(f"  Year range           : {stats['earliest_year']} - {stats['latest_year']}")
    print(f"  Unique languages     : {stats['languages']}")
    print(f"  Top movie            : {stats['top_movie']}  ({stats['top_movie_rating']:.2f})")
    if "highest_golden_score" in stats:
        print(f"  Highest GoldenScore  : {stats['highest_golden_score']:,.2f}")
        print(f"  Top Golden Movie     : {stats['top_golden_movie']}")

    print_header("Top 10 Highest-Rated Movies")
    print_table(highest_rated(df, 10))

    print_header("Top 10 Golden Index Score")
    gold = golden_leaderboard(df, 10)
    print_table(gold, cols=["rank", "title", "rating", "popularity", "vote_count", "GoldenScore"])

    print_header("Top 10 Hidden Gems")
    gems = hidden_gems(df, 10)
    if gems.empty:
        print("  No hidden gems found.\n")
    else:
        print_table(gems, cols=["title", "rating", "popularity", "GoldenScore"])

    return df


def interactive_menu(df: pd.DataFrame) -> None:
    while True:
        print_header("Menu")
        print("  1. Show Top 10 highest-rated")
        print("  2. Show Top 10 most popular")
        print("  3. Show Top 10 by vote count")
        print("  4. Search by movie title")
        print("  5. Filter by release year")
        print("  6. Sort all movies")
        print("  7. Show Golden Index Top 10")
        print("  8. Show Hidden Gems")
        print("  9. Quit")

        choice = input("\nChoose an option [1-9]: ").strip()

        if choice == "1":
            print_table(highest_rated(df, 10))

        elif choice == "2":
            print_table(most_popular(df, 10),
                        cols=["rank", "title", "popularity", "rating"])

        elif choice == "3":
            print_table(top_by_votes(df, 10),
                        cols=["rank", "title", "vote_count", "rating"])

        elif choice == "4":
            query = input("Enter movie title (partial OK): ").strip()
            result = search_by_title(df, query)
            if result.empty:
                print(f"\n  No movies matched '{query}'.\n")
            else:
                print(f"\nFound {len(result)} movie(s):")
                print_table(result, cols=["rank", "title", "release_year",
                                          "rating", "popularity", "GoldenScore",
                                          "original_language"])

        elif choice == "5":
            try:
                start = int(input("From year (e.g. 1990): ").strip())
                end = int(input("To year  (e.g. 2020): ").strip())
            except ValueError:
                print("  Please enter valid years.")
                continue
            filt = filter_by_year(df, start, end)
            print(f"\n{len(filt)} movie(s) released between {start} and {end}.\n")
            print_table(filt.head(20))

        elif choice == "6":
            print("\n  Available columns: rating | popularity | vote_count | release_year | GoldenScore")
            col = input("Sort by: ").strip() or "GoldenScore"
            order = input("Order [asc/desc]: ").strip().lower() or "desc"
            asc = order.startswith("a")
            sorted_df = sort_movies(df, by=col, ascending=asc)
            print_table(sorted_df.head(15))

        elif choice == "7":
            print_table(golden_leaderboard(df, 10),
                        cols=["title", "rating", "popularity", "vote_count", "GoldenScore"])

        elif choice == "8":
            gems = hidden_gems(df, 10)
            if gems.empty:
                print("\n  No hidden gems found in this dataset.\n")
            else:
                print(f"\nFound {len(gems)} hidden gem(s):")
                print_table(gems, cols=["title", "rating", "popularity", "GoldenScore"])

        elif choice == "9":
            print("\nThanks for using CineGold Movie Rating Analyzer.\n")
            break

        else:
            print("  Invalid choice. Please pick 1-9.")


if __name__ == "__main__":
    movies_df = run_analysis()

    if "--no-menu" in sys.argv:
        sys.exit(0)
    try:
        interactive_menu(movies_df)
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
