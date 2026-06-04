"""
search.py
---------
Tiny helper that lets the user search the local DataFrame by movie title.
Uses a case-insensitive substring match so partial words work too.
"""

import pandas as pd


def search_by_title(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """
    Return all movies whose title contains `query` (case-insensitive).

    Parameters
    ----------
    df : pd.DataFrame
        The full movie DataFrame.
    query : str
        Word or phrase to search for.
    """
    if not query or df.empty:
        return df.iloc[0:0]
    mask = df["title"].str.contains(query.strip(), case=False, na=False)
    return df[mask].reset_index(drop=True)
