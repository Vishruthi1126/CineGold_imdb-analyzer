"""
exporter.py
-----------
Export the analyzed DataFrame to CSV and PDF.
Includes GoldenScore column and auto-saves to exports/ folder.
"""

import io
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

EXPORTS_DIR = Path(__file__).parent / "exports"
DEFAULT_CSV = "movies_filtered.csv"
DEFAULT_PDF = "movie_analysis_report.pdf"


def _ensure_exports_dir() -> Path:
    """Create exports/ folder if it does not exist."""
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return EXPORTS_DIR


# ------------------------------------------------------------------ #
# CSV Export
# ------------------------------------------------------------------ #
def export_to_csv(df: pd.DataFrame, filename: str = "movies.csv") -> str:
    """
    Save the DataFrame to `filename`. Returns absolute path.
    Legacy function kept for CLI compatibility.
    """
    preferred_order = [
        "rank", "title", "release_year", "rating",
        "vote_count", "popularity", "original_language",
        "GoldenScore", "overview",
    ]
    columns = [c for c in preferred_order if c in df.columns]
    df[columns].to_csv(filename, index=False, encoding="utf-8")
    return os.path.abspath(filename)


def export_filtered_csv(df: pd.DataFrame) -> tuple[bytes, str]:
    """
    Export the filtered DataFrame (with GoldenScore) to CSV bytes for download
    and also auto-save to exports/ folder.

    Returns:
        (csv_bytes, saved_path)
    """
    _ensure_exports_dir()

    preferred_order = [
        "rank", "title", "catalog", "release_year", "rating",
        "vote_count", "popularity", "original_language",
        "GoldenScore", "overview",
    ]
    columns = [c for c in preferred_order if c in df.columns]
    export_df = df[columns].copy()

    buf = io.StringIO()
    export_df.to_csv(buf, index=False, encoding="utf-8")
    csv_str = buf.getvalue()
    csv_bytes = csv_str.encode("utf-8")

    save_path = EXPORTS_DIR / DEFAULT_CSV
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(csv_str)

    return csv_bytes, str(save_path)


# ------------------------------------------------------------------ #
# PDF Export
# ------------------------------------------------------------------ #
def export_pdf(
    df: pd.DataFrame,
    filters: dict | None = None,
    stats: dict | None = None,
) -> tuple[bytes, str]:
    """
    Export the filtered dataset to a PDF report using reportlab.

    Includes:
    - Project title
    - Export date and time
    - Applied filters
    - Summary statistics
    - Movie table with GoldenScore

    Returns:
        (pdf_bytes, saved_path)
    """
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
    except ImportError:
        raise RuntimeError(
            "reportlab is not installed. Run: pip install reportlab"
        )

    _ensure_exports_dir()
    save_path = EXPORTS_DIR / DEFAULT_PDF

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    GOLD_HEX = colors.HexColor("#C9A227")
    DARK_HEX = colors.HexColor("#1a1a1a")
    LIGHT_GOLD = colors.HexColor("#FDF8F0")

    title_style = ParagraphStyle(
        "GoldTitle", parent=styles["Title"],
        fontSize=22, textColor=GOLD_HEX, spaceAfter=4, alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        fontSize=11, textColor=DARK_HEX, spaceAfter=6, alignment=TA_CENTER,
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"],
        fontSize=13, textColor=GOLD_HEX, spaceBefore=12, spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=9, textColor=DARK_HEX, spaceAfter=3,
    )

    story = []

    story.append(Paragraph("CinéGold – Movie Rating Analyzer", title_style))
    story.append(Paragraph("Golden Index Score Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD_HEX, spaceAfter=8))

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"<b>Export Date & Time:</b> {now}", body_style))
    story.append(Spacer(1, 0.3 * cm))

    if filters:
        story.append(Paragraph("Applied Filters", section_style))
        for key, val in filters.items():
            story.append(Paragraph(f"  • <b>{key}:</b> {val}", body_style))
        story.append(Spacer(1, 0.3 * cm))

    if stats:
        story.append(Paragraph("Summary Statistics", section_style))
        stat_pairs = [
            ("Total Movies", stats.get("total_movies", "N/A")),
            ("Average Rating", stats.get("average_rating", "N/A")),
            ("Highest Rating", stats.get("highest_rating", "N/A")),
            ("Year Range", f"{stats.get('earliest_year', '?')} – {stats.get('latest_year', '?')}"),
            ("Languages", stats.get("languages", "N/A")),
            ("Top Movie", stats.get("top_movie", "N/A")),
        ]
        if "highest_golden_score" in stats:
            stat_pairs.append(("Highest GoldenScore", f"{stats['highest_golden_score']:,.2f}"))
            stat_pairs.append(("Top Golden Movie", stats.get("top_golden_movie", "N/A")))

        for label, value in stat_pairs:
            story.append(Paragraph(f"  • <b>{label}:</b> {value}", body_style))
        story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph(f"Movie Table ({len(df)} movies)", section_style))

    preferred_order = ["rank", "title", "release_year", "rating", "popularity", "vote_count", "GoldenScore", "original_language"]
    display_cols = [c for c in preferred_order if c in df.columns]
    header_labels = {
        "rank": "Rank", "title": "Title", "release_year": "Year",
        "rating": "Rating", "popularity": "Popularity",
        "vote_count": "Votes", "GoldenScore": "GoldenScore",
        "original_language": "Language",
    }

    table_data = [[header_labels.get(c, c) for c in display_cols]]
    for _, row in df[display_cols].head(100).iterrows():
        row_data = []
        for col in display_cols:
            val = row[col]
            if col == "title":
                val = str(val)[:35] + ("…" if len(str(val)) > 35 else "")
            elif col in ("rating", "popularity"):
                val = f"{float(val):.2f}" if pd.notna(val) else "N/A"
            elif col == "GoldenScore":
                val = f"{float(val):,.2f}" if pd.notna(val) else "N/A"
            elif col == "vote_count":
                val = f"{int(val):,}" if pd.notna(val) else "N/A"
            else:
                val = str(val) if pd.notna(val) else "N/A"
            row_data.append(val)
        table_data.append(row_data)

    col_widths = []
    for col in display_cols:
        if col == "title":
            col_widths.append(5.5 * cm)
        elif col in ("rank",):
            col_widths.append(1.0 * cm)
        elif col == "GoldenScore":
            col_widths.append(2.2 * cm)
        else:
            col_widths.append(1.8 * cm)

    tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD_HEX),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 1), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_GOLD, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#C9A227")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))

    story.append(tbl)

    if len(df) > 100:
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(f"Note: Showing first 100 of {len(df)} movies in this report.", body_style))

    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=GOLD_HEX))
    story.append(Paragraph("Data source: The Movie Database (TMDb) · Built with CinéGold", body_style))

    doc.build(story)
    pdf_bytes = buf.getvalue()

    with open(save_path, "wb") as f:
        f.write(pdf_bytes)

    return pdf_bytes, str(save_path)
