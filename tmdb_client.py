"""
tmdb_client.py
--------------
Handles communication with the TMDb (The Movie Database) public API.

Public functions
================
fetch_top_rated_movies(total_movies=250) -> list[dict]
fetch_tamil_movies(total_movies=250) -> list[dict]
fetch_all_movies(global_total=250, tamil_total=250) -> list[dict]
"""

import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TOP_RATED_ENDPOINT = "/movie/top_rated"
DISCOVER_ENDPOINT = "/discover/movie"
LANGUAGE_ENDPOINT = "/configuration/languages"
PAGE_SIZE = 20
DEFAULT_TIMEOUT = 15
MAX_RETRIES = 3


def _get_api_key() -> str:
    api_key = os.environ.get("TMDB_API_KEY", "").strip().strip('"').strip("'")
    if not api_key or api_key == "your_tmdb_api_key_here":
        raise RuntimeError(
            "TMDB_API_KEY is missing.\n"
            "1) Copy '.env.example' to '.env'\n"
            "2) Put your real TMDb API key in the TMDB_API_KEY variable\n"
            "3) Get a free key at https://www.themoviedb.org/settings/api"
        )
    if len(api_key) < 20:
        raise RuntimeError(
            "TMDB_API_KEY looks too short — you may have pasted the API Key ID "
            "instead of the full 'API Key (v3 auth)'.\n"
            "At https://www.themoviedb.org/settings/api, copy the long v3 key "
            "(about 32 characters), not the short numeric ID."
        )
    return api_key


def _safe_request(url: str, params: dict) -> dict:
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
            if response.status_code == 401:
                raise RuntimeError("TMDb rejected the API key (HTTP 401). "
                                   "Check that TMDB_API_KEY is correct.")
            if response.status_code == 429:
                wait = int(response.headers.get("Retry-After", "2"))
                time.sleep(wait + 1)
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as err:
            last_error = err
            time.sleep(2 * attempt)
        except requests.exceptions.Timeout as err:
            last_error = err
            time.sleep(2 * attempt)
        except requests.exceptions.RequestException as err:
            last_error = err
            break
    raise RuntimeError(f"Network error while contacting TMDb: {last_error}")


_LANGUAGE_CACHE: dict[str, str] | None = None


def _load_language_map() -> dict[str, str]:
    global _LANGUAGE_CACHE
    if _LANGUAGE_CACHE is not None:
        return _LANGUAGE_CACHE
    try:
        data = _safe_request(
            TMDB_BASE_URL + LANGUAGE_ENDPOINT,
            {"api_key": _get_api_key()},
        )
        _LANGUAGE_CACHE = {item["iso_639_1"]: item.get("english_name", item["iso_639_1"])
                           for item in data}
    except Exception:
        _LANGUAGE_CACHE = {}
    return _LANGUAGE_CACHE


def _parse_movie(raw: dict, *, catalog: str, language_map: dict[str, str]) -> dict:
    release_year = (raw.get("release_date") or "0000")[:4]
    try:
        release_year_int = int(release_year)
    except ValueError:
        release_year_int = None

    lang_code = raw.get("original_language") or ""
    return {
        "tmdb_id": int(raw.get("id") or 0),
        "catalog": catalog,
        "title": raw.get("title") or raw.get("original_title") or "Unknown",
        "release_year": release_year_int,
        "rating": float(raw.get("vote_average") or 0.0),
        "vote_count": int(raw.get("vote_count") or 0),
        "popularity": float(raw.get("popularity") or 0.0),
        "original_language": language_map.get(lang_code, lang_code or "n/a"),
        "overview": (raw.get("overview") or "").strip(),
    }


def _paginate_movies(
    *,
    url: str,
    base_params: dict,
    total_movies: int,
    catalog: str,
    language_map: dict[str, str],
    verbose: bool,
    label: str,
) -> list[dict]:
    movies: list[dict] = []
    pages_needed = (total_movies + PAGE_SIZE - 1) // PAGE_SIZE
    if verbose:
        print(f"Fetching {total_movies} {label} across {pages_needed} pages ...")

    for page in range(1, pages_needed + 1):
        params = {**base_params, "page": page}
        data = _safe_request(url, params)
        results = data.get("results") or []
        if not results:
            if verbose:
                print(f"  No more {label} results on page {page} - stopping early.")
            break

        for raw in results:
            movies.append(_parse_movie(raw, catalog=catalog, language_map=language_map))
            if len(movies) >= total_movies:
                break

        if verbose:
            print(f"  {label} page {page}/{pages_needed}  ->  {len(movies)} movies")

        if len(movies) >= total_movies:
            break
        time.sleep(0.25)

    if verbose:
        print(f"Done. {label}: {len(movies)} movies")
    return movies


def fetch_top_rated_movies(total_movies: int = 250, verbose: bool = True) -> list[dict]:
    api_key = _get_api_key()
    language_map = _load_language_map()
    movies = _paginate_movies(
        url=TMDB_BASE_URL + TOP_RATED_ENDPOINT,
        base_params={"api_key": api_key, "language": "en-US"},
        total_movies=total_movies,
        catalog="Global Top Rated",
        language_map=language_map,
        verbose=verbose,
        label="global top-rated",
    )
    for i, movie in enumerate(movies, start=1):
        movie["rank"] = i
    return movies


def fetch_tamil_movies(total_movies: int = 250, verbose: bool = True) -> list[dict]:
    api_key = _get_api_key()
    language_map = _load_language_map()
    movies = _paginate_movies(
        url=TMDB_BASE_URL + DISCOVER_ENDPOINT,
        base_params={
            "api_key": api_key,
            "language": "en-US",
            "with_original_language": "ta",
            "sort_by": "vote_average.desc",
            "vote_count.gte": 50,
            "include_adult": "false",
        },
        total_movies=total_movies,
        catalog="Tamil Cinema",
        language_map=language_map,
        verbose=verbose,
        label="Tamil cinema",
    )
    for i, movie in enumerate(movies, start=1):
        movie["rank"] = i
    return movies


def fetch_all_movies(
    global_total: int = 250,
    tamil_total: int = 250,
    include_tamil: bool = True,
    verbose: bool = True,
) -> list[dict]:
    global_movies = fetch_top_rated_movies(global_total, verbose=verbose)
    if not include_tamil or tamil_total <= 0:
        return global_movies

    tamil_movies = fetch_tamil_movies(tamil_total, verbose=verbose)
    by_id: dict[int, dict] = {}

    for movie in global_movies:
        mid = movie.get("tmdb_id") or 0
        if mid:
            by_id[mid] = movie

    for movie in tamil_movies:
        mid = movie.get("tmdb_id") or 0
        if not mid:
            continue
        if mid in by_id:
            by_id[mid]["catalog"] = "Global & Tamil"
            if movie["rating"] > by_id[mid]["rating"]:
                by_id[mid]["rating"] = movie["rating"]
            by_id[mid]["vote_count"] = max(by_id[mid]["vote_count"], movie["vote_count"])
        else:
            by_id[mid] = movie

    merged = list(by_id.values())
    merged.sort(key=lambda m: (m["rating"], m["vote_count"]), reverse=True)
    for i, movie in enumerate(merged, start=1):
        movie["rank"] = i
    return merged
