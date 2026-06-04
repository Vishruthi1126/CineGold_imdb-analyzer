"""
app.py
------
Streamlit web dashboard for CineGold - Movie Rating Analyzer.
Enhanced with Golden Index Score, Hidden Gems, PDF export, and more.

Launch with:
    streamlit run app.py
"""

import io
from pathlib import Path

import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from auth import init_session, render_auth_page, logout
from styles import apply_theme
from tmdb_client import fetch_all_movies
from analyzer import (
    to_dataframe, highest_rated, most_popular, top_by_votes,
    summary_stats, filter_by_year, filter_by_catalog, sort_movies,
    calculate_golden_score, golden_leaderboard, hidden_gems,
)
from visualizer import (
    plot_top_rated_bytes, plot_rating_distribution_bytes,
    plot_movies_per_year_bytes, plot_popularity_bytes,
    plot_golden_score_top10, plot_hidden_gems, plot_golden_distribution,
)
from exporter import export_filtered_csv, export_pdf
from search import search_by_title


load_dotenv(Path(__file__).resolve().parent / ".env")

st.set_page_config(
    page_title="CineGold - Movie Rating Analyzer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()


@st.cache_data(show_spinner="Fetching global & Tamil cinema from TMDb...", ttl=60 * 60)
def load_movies(global_total: int, tamil_total: int, include_tamil: bool) -> pd.DataFrame:
    raw = fetch_all_movies(
        global_total=global_total,
        tamil_total=tamil_total,
        include_tamil=include_tamil,
        verbose=False,
    )
    df = to_dataframe(raw)
    df = calculate_golden_score(df)
    return df


def render_metric_card(col, label: str, value, sub: str = "") -> None:
    with col:
        st.markdown(
            f"<div class='metric-card'><h3>{value}</h3><p>{label}</p>"
            + (f"<span style='font-size:0.75rem;opacity:0.7'>{sub}</span>" if sub else "")
            + "</div>",
            unsafe_allow_html=True,
        )


def render_dashboard() -> None:
    """Main analyzer UI (shown after login)."""
    with st.sidebar:
        st.title("🎬 CineGold")
        user = st.session_state.get("username", "Guest")
        st.caption(f"Signed in as **{user}**")

        if st.button("Sign out", use_container_width=True):
            logout()
            st.rerun()

        st.markdown("---")
        st.caption("Global top-rated · Tamil cinema")

        theme = st.radio("Theme", ["Light", "Dark"], horizontal=True)
        apply_theme(theme)

        st.markdown("---")
        st.markdown("**Catalog**")
        include_tamil = st.checkbox("Include Tamil cinema (Kollywood)", value=True)
        total_movies = st.slider(
            "Global top-rated count",
            min_value=50, max_value=500, value=250, step=50,
        )
        tamil_movies = st.slider(
            "Tamil movies to fetch",
            min_value=50, max_value=500, value=250, step=50,
            disabled=not include_tamil,
        )

        if st.button("Reload data from TMDb"):
            st.cache_data.clear()

        st.markdown("---")
        st.markdown("**Quick links**")
        st.markdown("- [Get TMDb API key](https://www.themoviedb.org/settings/api)")
        st.markdown("- [TMDb top-rated list](https://www.themoviedb.org/movie/top-rated)")

    st.title("Movie Rating Analyzer")
    st.markdown(
        '<p class="hero-tagline">World cinema & Tamil classics — curated in gold</p>',
        unsafe_allow_html=True,
    )
    st.write(
        "Explore the highest-rated films worldwide **and** Kollywood's finest, "
        "sourced live from TMDb. Filter by catalog, year, and title — then download your picks."
    )
    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)

    try:
        df = load_movies(total_movies, tamil_movies, include_tamil)
    except RuntimeError as err:
        st.error(f"Could not fetch data: {err}")
        return

    if df.empty:
        st.warning("TMDb returned no movies. Try again later.")
        return

    tamil_count = (
        int(df["catalog"].astype(str).str.contains("Tamil", case=False, na=False).sum())
        if "catalog" in df.columns else 0
    )
    st.caption(f"Loaded **{len(df)}** titles · **{tamil_count}** Tamil / Kollywood entries")

    years = df["release_year"].dropna().astype(int)
    min_year, max_year = int(years.min()), int(years.max())

    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
    with c1:
        catalog_filter = st.selectbox(
            "Catalog",
            ["All", "Global Top Rated", "Tamil Cinema", "Global & Tamil"],
        )
    with c2:
        year_range = st.slider(
            "Release year range",
            min_value=min_year, max_value=max_year,
            value=(min_year, max_year),
        )
    with c3:
        sort_options = ["GoldenScore", "rating", "popularity", "vote_count", "release_year"]
        sort_col = st.selectbox("Sort by", sort_options)
    with c4:
        query = st.text_input("Search movie title", placeholder="e.g. Vikram, Godfather")

    filtered = filter_by_catalog(df, catalog_filter)
    filtered = filter_by_year(filtered, year_range[0], year_range[1])
    if query:
        filtered = search_by_title(filtered, query)
    filtered = sort_movies(filtered, by=sort_col, ascending=False)

    # Ensure GoldenScore is present in filtered
    if "GoldenScore" not in filtered.columns:
        filtered = calculate_golden_score(filtered)

    stats = summary_stats(filtered if not filtered.empty else df)

    # ---- 4 Metric cards ----
    m1, m2, m3, m4 = st.columns(4)
    render_metric_card(m1, "Total Movies", stats.get("total_movies", 0))
    render_metric_card(m2, "Average Rating", stats.get("average_rating", "N/A"))

    if "highest_golden_score" in stats:
        render_metric_card(
            m3, "Highest GoldenScore",
            f"{stats['highest_golden_score']:,.1f}",
        )
        render_metric_card(
            m4, "Top Golden Movie",
            stats.get("top_golden_movie", "N/A"),
            sub=f"Score: {stats.get('top_golden_score_value', 0):,.1f}",
        )
    else:
        render_metric_card(m3, "Top Movie", stats.get("top_movie", "N/A"))
        render_metric_card(
            m4, "Year Range",
            f"{stats.get('earliest_year', '?')} – {stats.get('latest_year', '?')}",
        )

    st.markdown("&nbsp;")

    # ---- Tabs ----
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Charts",
        "📋 Table",
        "🏆 Leaderboards",
        "🥇 Golden Index Ranking",
        "💎 Hidden Gems",
        "📥 Export & Reports",
    ])

    # ---- Tab 1: Charts ----
    with tab1:
        if filtered.empty:
            st.info("No movies match the current filters — adjust them to see charts.")
        else:
            ch1, ch2 = st.columns(2)
            with ch1:
                st.image(plot_top_rated_bytes(filtered), use_container_width=True)
                st.image(plot_movies_per_year_bytes(filtered), use_container_width=True)
                st.image(plot_golden_distribution(filtered), use_container_width=True)
            with ch2:
                st.image(plot_rating_distribution_bytes(filtered), use_container_width=True)
                st.image(plot_popularity_bytes(filtered), use_container_width=True)
                st.image(plot_golden_score_top10(filtered), use_container_width=True)

    # ---- Tab 2: Table ----
    with tab2:
        st.subheader(f"{len(filtered)} movie(s) shown")
        table_cols = [
            "rank", "title", "catalog", "release_year", "rating", "vote_count",
            "popularity", "GoldenScore", "original_language", "overview",
        ]
        display_cols = [c for c in table_cols if c in filtered.columns]
        st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)
        st.caption("Go to the **📥 Export & Reports** tab to download CSV or PDF.")

    # ---- Tab 3: Leaderboards ----
    with tab3:
        cA, cB, cC = st.columns(3)
        with cA:
            st.markdown("#### ⭐ Highest rated")
            cols = ["title", "rating", "catalog"] if "catalog" in filtered.columns else ["title", "rating"]
            st.dataframe(highest_rated(filtered, 10)[cols], hide_index=True, use_container_width=True)
        with cB:
            st.markdown("#### 🔥 Most popular")
            st.dataframe(
                most_popular(filtered, 10)[["title", "popularity"]],
                hide_index=True, use_container_width=True,
            )
        with cC:
            st.markdown("#### 👥 Top by votes")
            st.dataframe(
                top_by_votes(filtered, 10)[["title", "vote_count"]],
                hide_index=True, use_container_width=True,
            )

    # ---- Tab 4: Golden Index Ranking ----
    with tab4:
        st.subheader("🏆 Golden Index Ranking")
        st.markdown(
            """
            The **CineGold Golden Index Score** is a custom ranking algorithm that combines:
            - **Rating × 50** — quality weight
            - **Popularity × 0.3** — audience reach
            - **Vote Count × 0.2** — credibility

            `GoldenScore = (Rating × 50) + (Popularity × 0.3) + (VoteCount × 0.2)`
            """,
            unsafe_allow_html=False,
        )

        if filtered.empty:
            st.info("No movies match the current filters.")
        else:
            gold_df = golden_leaderboard(filtered, 10)
            gold_cols = ["title", "rating", "popularity", "vote_count", "GoldenScore"]
            if "catalog" in gold_df.columns:
                gold_cols = ["title", "catalog", "rating", "popularity", "vote_count", "GoldenScore"]
            gold_display = [c for c in gold_cols if c in gold_df.columns]

            st.markdown("#### Top 10 by GoldenScore")
            st.dataframe(gold_df[gold_display], hide_index=True, use_container_width=True)

            st.markdown("---")
            st.image(plot_golden_score_top10(filtered), use_container_width=True)
            st.image(plot_golden_distribution(filtered), use_container_width=True)

            st.markdown("---")
            st.markdown("#### Full GoldenScore Table")
            all_gold = filtered.sort_values("GoldenScore", ascending=False).reset_index(drop=True)
            all_gold_cols = [c for c in gold_cols if c in all_gold.columns]
            st.dataframe(all_gold[all_gold_cols], hide_index=True, use_container_width=True)

    # ---- Tab 5: Hidden Gems ----
    with tab5:
        st.subheader("💎 Hidden Gems Detector")
        st.markdown(
            """
            **Hidden Gems** are underrated masterpieces the world hasn't noticed enough:
            - **Rating ≥ 8.0** — critically acclaimed
            - **Popularity < dataset average** — under the radar

            These films deserve more attention!
            """,
        )

        if filtered.empty:
            st.info("No movies match the current filters.")
        else:
            avg_pop = filtered["popularity"].mean()
            gems = hidden_gems(filtered, 10)

            if gems.empty:
                st.warning(
                    "No hidden gems found in the current filter. "
                    f"Average popularity threshold is {avg_pop:.1f}. "
                    "Try expanding your filters."
                )
            else:
                st.caption(f"Average popularity in current filter: **{avg_pop:.2f}** · Found **{len(gems)}** hidden gems")

                gems_cols = ["title", "rating", "popularity", "vote_count", "GoldenScore"]
                if "catalog" in gems.columns:
                    gems_cols = ["title", "catalog", "rating", "popularity", "vote_count", "GoldenScore"]
                gems_display = [c for c in gems_cols if c in gems.columns]

                st.dataframe(gems[gems_display], hide_index=True, use_container_width=True)
                st.markdown("---")
                st.image(plot_hidden_gems(filtered), use_container_width=True)

                st.markdown("---")
                st.markdown("#### Why These Films Are Hidden Gems")
                for _, row in gems.iterrows():
                    with st.expander(f"💎 {row['title']} ({row.get('release_year', 'N/A')})"):
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Rating", f"{row['rating']:.2f}")
                        c2.metric("Popularity", f"{row['popularity']:.1f}")
                        c3.metric("Votes", f"{int(row['vote_count']):,}")
                        c4.metric("GoldenScore", f"{row['GoldenScore']:,.1f}")
                        if "overview" in row and row["overview"]:
                            st.caption(row["overview"][:300] + ("..." if len(str(row["overview"])) > 300 else ""))

    # ---- Tab 6: Export & Reports ----
    with tab6:
        st.subheader("📥 Export & Download Reports")
        st.markdown("Download your current filtered dataset as a **CSV** or a styled **PDF analysis report**.")
        st.markdown("---")

        if filtered.empty:
            st.warning("No movies match the current filters. Adjust filters to enable export.")
        else:
            filters_info = {
                "Catalog": catalog_filter,
                "Year Range": f"{year_range[0]} – {year_range[1]}",
                "Search": query if query else "None",
                "Sort By": sort_col,
            }

            # ── Summary card ──────────────────────────────────────────────
            s1, s2, s3 = st.columns(3)
            s1.metric("Movies in export", len(filtered))
            s2.metric("Avg Rating", f"{filtered['rating'].mean():.2f}")
            s3.metric("Avg GoldenScore", f"{filtered['GoldenScore'].mean():,.0f}")
            st.markdown("---")

            # ── CSV Download ──────────────────────────────────────────────
            st.markdown("### 📄 CSV Export")
            st.markdown("All movies with rank, title, rating, votes, popularity, GoldenScore and overview.")
            csv_bytes, csv_path = export_filtered_csv(filtered)
            st.download_button(
                label="📥 Download Filtered CSV",
                data=csv_bytes,
                file_name="cinegold_movies.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.caption(f"Contains {len(filtered)} rows · auto-saved to `{csv_path}`")

            st.markdown("---")

            # ── PDF Download ──────────────────────────────────────────────
            st.markdown("### 📑 PDF Analysis Report")
            st.markdown("Gold-styled landscape report with summary stats, top films table, and GoldenScore rankings.")
            try:
                pdf_bytes, pdf_path = export_pdf(filtered, filters=filters_info, stats=stats)
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_bytes,
                    file_name="cinegold_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
                st.caption(f"Landscape A4 · gold-styled · auto-saved to `{pdf_path}`")
            except Exception as e:
                st.error(f"PDF generation failed: {e}")

            st.markdown("---")

            # ── Auto-Save both ─────────────────────────────────────────────
            st.markdown("### 💾 Auto-Save Both to Server")
            st.markdown("Saves CSV + PDF directly to the `exports/` folder on this server.")
            if st.button("💾 Save CSV + PDF to exports/ folder", use_container_width=True):
                with st.spinner("Saving…"):
                    try:
                        _, c = export_filtered_csv(filtered)
                        _, p = export_pdf(filtered, filters=filters_info, stats=stats)
                        st.success(f"✅ Saved!\n- **CSV** → `{c}`\n- **PDF** → `{p}`")
                    except Exception as e:
                        st.error(f"Save failed: {e}")

    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
    st.caption("Data: themoviedb.org · Global top-rated & Tamil discover API · Built with Streamlit")


# --------------------------------------------------------------------- #
# Entry: auth gate -> dashboard
# --------------------------------------------------------------------- #
if not st.session_state.get("authenticated"):
    render_auth_page()
else:
    render_dashboard()
