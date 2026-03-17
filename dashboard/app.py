"""
דשבורד נתוני בריאות - משרד הבריאות
עיצוב בהשראת me.health.gov.il / health.gov.il
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# ─────────────────────────────────────────────
# PAGE CONFIG - must be first Streamlit call
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="נתוני בריאות | משרד הבריאות",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# DESIGN SYSTEM — משרד הבריאות
# ─────────────────────────────────────────────
COLORS = {
    "primary":    "#0E4780",   # כחול כהה — ראשי
    "secondary":  "#1B85C8",   # כחול בינוני
    "teal":       "#2D9C9C",   # ירוק-כחול (נפש בריאה)
    "teal_light": "#E6F6F6",
    "blue_light": "#EEF4FB",
    "white":      "#FFFFFF",
    "bg":         "#F4F8FC",
    "border":     "#C8D8EC",
    "text":       "#1A2840",
    "text_muted": "#4A6080",
    "success":    "#2A8C5A",
    "warning":    "#D4760A",
    "error":      "#C0392B",
}

MOH_CSS = f"""
<style>
  /* ─── גופן עברי ─── */
  @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {{
    font-family: 'Rubik', 'Arial Hebrew', Arial, sans-serif;
    direction: rtl;
    color: {COLORS['text']};
  }}

  /* ─── רקע ─── */
  .stApp {{
    background-color: {COLORS['bg']};
  }}

  /* ─── Sidebar ─── */
  [data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {COLORS['primary']} 0%, #0A3560 100%);
    direction: rtl;
  }}
  [data-testid="stSidebar"] * {{
    color: {COLORS['white']} !important;
    direction: rtl;
  }}
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stTextInput label,
  [data-testid="stSidebar"] .stCheckbox label {{
    color: #B8D0EC !important;
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 0.03em;
  }}
  [data-testid="stSidebar"] .stSelectbox > div > div {{
    background: rgba(255,255,255,0.12) !important;
    border-color: rgba(255,255,255,0.25) !important;
    color: white !important;
  }}

  /* ─── Header ─── */
  .moh-header {{
    background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
    padding: 1.25rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 4px 20px rgba(14,71,128,0.25);
  }}
  .moh-header h1 {{
    color: white;
    margin: 0;
    font-size: 1.6rem;
    font-weight: 700;
    text-shadow: 0 1px 3px rgba(0,0,0,0.2);
  }}
  .moh-header p {{
    color: rgba(255,255,255,0.8);
    margin: 0;
    font-size: 0.9rem;
    font-weight: 300;
  }}
  .moh-logo-img {{
    height: 56px;
    width: auto;
    filter: brightness(0) invert(1);
    flex-shrink: 0;
  }}

  /* ─── כרטיסי מדד (KPI cards) ─── */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }}
  .kpi-card {{
    background: {COLORS['white']};
    border-radius: 12px;
    padding: 1.25rem 1rem;
    text-align: center;
    border: 1px solid {COLORS['border']};
    box-shadow: 0 2px 12px rgba(14,71,128,0.07);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }}
  .kpi-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(14,71,128,0.13);
  }}
  .kpi-value {{
    font-size: 2rem;
    font-weight: 700;
    color: {COLORS['primary']};
    line-height: 1.1;
  }}
  .kpi-label {{
    font-size: 0.78rem;
    color: {COLORS['text_muted']};
    margin-top: 0.3rem;
    font-weight: 500;
  }}
  .kpi-card.teal .kpi-value {{ color: {COLORS['teal']}; }}
  .kpi-card.green .kpi-value {{ color: {COLORS['success']}; }}
  .kpi-card.orange .kpi-value {{ color: {COLORS['warning']}; }}

  /* ─── כרטיס תוכן ─── */
  .content-card {{
    background: {COLORS['white']};
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid {COLORS['border']};
    box-shadow: 0 2px 12px rgba(14,71,128,0.06);
    margin-bottom: 1rem;
  }}
  .card-title {{
    font-size: 1rem;
    font-weight: 600;
    color: {COLORS['primary']};
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid {COLORS['teal']};
    display: inline-block;
  }}

  /* ─── תגיות (badges) ─── */
  .badge {{
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    margin: 0 2px;
  }}
  .badge-blue {{ background: {COLORS['blue_light']}; color: {COLORS['primary']}; }}
  .badge-teal {{ background: {COLORS['teal_light']}; color: {COLORS['teal']}; }}
  .badge-green {{ background: #E8F6ED; color: {COLORS['success']}; }}

  /* ─── שורת מאגר ─── */
  .dataset-row {{
    padding: 0.9rem 1rem;
    border-radius: 8px;
    border: 1px solid {COLORS['border']};
    margin-bottom: 0.6rem;
    background: {COLORS['white']};
    transition: border-color 0.15s;
  }}
  .dataset-row:hover {{
    border-color: {COLORS['secondary']};
    background: {COLORS['blue_light']};
  }}
  .dataset-title {{
    font-weight: 600;
    font-size: 0.92rem;
    color: {COLORS['primary']};
  }}
  .dataset-meta {{
    font-size: 0.78rem;
    color: {COLORS['text_muted']};
    margin-top: 0.2rem;
  }}

  /* ─── כפתור ─── */
  .stButton > button {{
    background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']}) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.4rem !important;
    font-family: 'Rubik', Arial, sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    transition: opacity 0.15s ease !important;
    box-shadow: 0 2px 8px rgba(14,71,128,0.25) !important;
  }}
  .stButton > button:hover {{
    opacity: 0.88 !important;
  }}

  /* ─── input boxes ─── */
  .stTextInput > div > div > input,
  .stSelectbox > div > div {{
    border-radius: 8px !important;
    border-color: {COLORS['border']} !important;
    direction: rtl !important;
  }}
  .stTextInput label, .stSelectbox label, .stMultiSelect label {{
    font-weight: 500 !important;
    color: {COLORS['text']} !important;
    direction: rtl !important;
  }}

  /* ─── Plotly charts border ─── */
  [data-testid="stPlotlyChart"] {{
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid {COLORS['border']};
  }}

  /* ─── טבלה ─── */
  .stDataFrame {{
    border-radius: 8px !important;
    overflow: hidden;
    direction: rtl;
  }}

  /* ─── כותרות חלקים ─── */
  .section-header {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 1.5rem 0 1rem 0;
  }}
  .section-header h2 {{
    font-size: 1.1rem;
    font-weight: 700;
    color: {COLORS['primary']};
    margin: 0;
  }}
  .section-divider {{
    flex: 1;
    height: 2px;
    background: linear-gradient(to left, transparent, {COLORS['border']});
    margin-right: 0.5rem;
  }}

  /* ─── Footer ─── */
  .moh-footer {{
    text-align: center;
    padding: 1rem;
    margin-top: 2rem;
    border-top: 1px solid {COLORS['border']};
    font-size: 0.78rem;
    color: {COLORS['text_muted']};
  }}
  .moh-footer a {{
    color: {COLORS['secondary']};
    text-decoration: none;
  }}

  /* ─── hide Streamlit chrome ─── */
  #MainMenu {{ visibility: hidden; }}
  footer {{ visibility: hidden; }}
  header {{ visibility: hidden; }}
  .block-container {{ padding-top: 1.5rem !important; }}
</style>
"""

# ─────────────────────────────────────────────
# DATA FUNCTIONS
# ─────────────────────────────────────────────
BASE_URL = "https://data.gov.il/api/3/action"
ORG = "ministry-health"
RAW_DIR = Path(__file__).parent.parent / "data" / "raw"

@st.cache_data(ttl=3600, show_spinner=False)
def load_datasets() -> pd.DataFrame:
    """שולף מכל מאגרי משרד הבריאות"""
    try:
        resp = requests.get(
            f"{BASE_URL}/package_search",
            params={"fq": f"organization:{ORG}", "rows": 1000, "start": 0},
            timeout=30,
        )
        resp.raise_for_status()
        results = resp.json()["result"]["results"]
        rows = []
        for ds in results:
            rows.append({
                "id":       ds.get("id", ""),
                "name":     ds.get("name", ""),
                "title":    ds.get("title", ""),
                "notes":    (ds.get("notes") or "")[:120],
                "resources": len(ds.get("resources", [])),
                "tags":     ", ".join(t["display_name"] for t in ds.get("tags", [])[:4]),
                "modified": (ds.get("metadata_modified") or "")[:10],
                "formats":  ", ".join({
                    r.get("format", "?").upper()
                    for r in ds.get("resources", [])
                    if r.get("format")
                }),
            })
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"שגיאה בשליפת נתונים: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def load_local_csv() -> pd.DataFrame:
    """טוען CSV שמור אם קיים"""
    path = RAW_DIR / "datasets_list.csv"
    if path.exists():
        return pd.read_csv(path, encoding="utf-8-sig")
    return pd.DataFrame()


def kpi_card(value, label, variant="") -> str:
    return (
        f'<div class="kpi-card {variant}">'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-label">{label}</div>'
        f'</div>'
    )


def section_header(icon: str, title: str) -> str:
    return (
        f'<div class="section-header">'
        f'<h2>{icon} {title}</h2>'
        f'<div class="section-divider"></div>'
        f'</div>'
    )


# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────
def main():
    st.markdown(MOH_CSS, unsafe_allow_html=True)

    # ── SIDEBAR ──
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 1rem 0 1.5rem;">
          <img src="https://www.gov.il/media/224edbtw/logo-desktop-header.svg"
               alt="משרד הבריאות"
               style="max-width:140px; filter:brightness(0) invert(1); margin-bottom:0.4rem;">
          <div style="font-size:0.78rem; color:rgba(255,255,255,0.6); margin-top:0.2rem">
            פורטל נתוני בריאות
          </div>
        </div>
        <hr style="border-color:rgba(255,255,255,0.2); margin-bottom:1.2rem">
        """, unsafe_allow_html=True)

        page = st.selectbox(
            "ניווט",
            ["סקירה כללית", "מאגרי נתונים", "ניתוח"],
            label_visibility="collapsed",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.78rem; color:rgba(255,255,255,0.5); text-transform:uppercase; letter-spacing:.05em">סינון</div>', unsafe_allow_html=True)

        search_term = st.text_input("חיפוש מאגר", placeholder="הקלד לחיפוש...")
        show_csv_only = st.checkbox("קבצי CSV בלבד")
        show_updated = st.checkbox("עודכנו ב-2024+")

        st.markdown("<br>", unsafe_allow_html=True)
        refresh = st.button("⟳  רענן נתונים")

        st.markdown("""
        <div style="position:absolute; bottom:1.5rem; left:0; right:0; text-align:center;
                    font-size:0.72rem; color:rgba(255,255,255,0.35);">
          מקור: data.gov.il
        </div>
        """, unsafe_allow_html=True)

    # ── LOAD DATA ──
    if refresh:
        st.cache_data.clear()

    with st.spinner("טוען נתונים מ-data.gov.il..."):
        df = load_datasets()
        if df.empty:
            df = load_local_csv()

    if df.empty:
        st.warning("לא נמצאו נתונים. לחץ 'רענן נתונים' כדי לשלוף מה-API.")
        return

    # ── APPLY FILTERS ──
    filtered = df.copy()
    if search_term:
        mask = (
            filtered["title"].str.contains(search_term, case=False, na=False)
            | filtered["notes"].str.contains(search_term, case=False, na=False)
            | filtered["tags"].str.contains(search_term, case=False, na=False)
        )
        filtered = filtered[mask]
    if show_csv_only and "formats" in filtered.columns:
        filtered = filtered[filtered["formats"].str.contains("CSV", na=False)]
    if show_updated and "modified" in filtered.columns:
        filtered = filtered[filtered["modified"] >= "2024"]

    # ════════════════════════════════════════
    # PAGE: סקירה כללית
    # ════════════════════════════════════════
    if page == "סקירה כללית":
        # Header
        st.markdown("""
        <div class="moh-header">
          <img src="https://www.gov.il/media/224edbtw/logo-desktop-header.svg"
               alt="משרד הבריאות" class="moh-logo-img">
          <div>
            <h1>נתוני בריאות — ישראל</h1>
            <p>מאגרי מידע של משרד הבריאות · פורטל הנתונים הפתוחים</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # KPIs
        total = len(df)
        csv_count = int(df["formats"].str.contains("CSV", na=False).sum()) if "formats" in df.columns else 0
        updated_2024 = int((df["modified"] >= "2024").sum()) if "modified" in df.columns else 0
        total_res = int(df["resources"].sum()) if "resources" in df.columns else 0

        st.markdown(
            '<div class="kpi-grid">'
            + kpi_card(f"{total:,}", "מאגרי נתונים סה\"כ")
            + kpi_card(f"{total_res:,}", "קבצי מידע", "teal")
            + kpi_card(f"{csv_count:,}", "קבצי CSV", "green")
            + kpi_card(f"{updated_2024:,}", "עודכנו 2024+", "orange")
            + '</div>',
            unsafe_allow_html=True,
        )

        # Charts row
        col1, col2 = st.columns([3, 2], gap="medium")

        with col1:
            st.markdown(section_header("📊", "פורמטים נפוצים"), unsafe_allow_html=True)
            if "formats" in df.columns:
                fmt_series = (
                    df["formats"]
                    .str.split(", ")
                    .explode()
                    .str.strip()
                    .replace("", pd.NA)
                    .dropna()
                    .value_counts()
                    .head(8)
                )
                fig = go.Figure(go.Bar(
                    x=fmt_series.values,
                    y=fmt_series.index,
                    orientation="h",
                    marker_color=[COLORS["primary"], COLORS["secondary"], COLORS["teal"],
                                  "#4AAED4", "#7BC4E2", "#A8D8EA", "#C8E8F2", "#E0F2F8"],
                    text=fmt_series.values,
                    textposition="outside",
                ))
                fig.update_layout(
                    height=280,
                    margin=dict(l=10, r=30, t=10, b=10),
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    xaxis=dict(showgrid=True, gridcolor="#EEF4FB", zeroline=False),
                    yaxis=dict(showgrid=False),
                    font=dict(family="Rubik, Arial", size=12, color=COLORS["text"]),
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(section_header("📅", "פעילות לפי שנה"), unsafe_allow_html=True)
            if "modified" in df.columns:
                year_counts = (
                    df["modified"]
                    .str[:4]
                    .replace("", pd.NA)
                    .dropna()
                    .value_counts()
                    .sort_index()
                )
                colors_bar = [
                    COLORS["teal"] if y >= "2024" else COLORS["secondary"]
                    for y in year_counts.index
                ]
                fig2 = go.Figure(go.Bar(
                    x=year_counts.index,
                    y=year_counts.values,
                    marker_color=colors_bar,
                    text=year_counts.values,
                    textposition="outside",
                ))
                fig2.update_layout(
                    height=280,
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="#EEF4FB", zeroline=False),
                    font=dict(family="Rubik, Arial", size=12, color=COLORS["text"]),
                )
                st.plotly_chart(fig2, use_container_width=True)

        # Recent datasets
        st.markdown(section_header("🗂️", "מאגרים אחרונים"), unsafe_allow_html=True)
        recent = df.sort_values("modified", ascending=False).head(5)
        for _, row in recent.iterrows():
            fmt_badge = "".join(
                f'<span class="badge badge-teal">{f.strip()}</span>'
                for f in str(row.get("formats", "")).split(",")
                if f.strip()
            )
            st.markdown(f"""
            <div class="dataset-row">
              <div class="dataset-title">{row.get('title', row.get('name', ''))}</div>
              <div class="dataset-meta">
                {fmt_badge}
                <span class="badge badge-blue">📁 {row.get('resources', 0)} קבצים</span>
                <span style="color:{COLORS['text_muted']}; font-size:0.75rem; margin-right:0.5rem">
                  עודכן: {row.get('modified', '—')}
                </span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ════════════════════════════════════════
    # PAGE: מאגרי נתונים
    # ════════════════════════════════════════
    elif page == "מאגרי נתונים":
        st.markdown("""
        <div class="moh-header">
          <div class="moh-logo">🗂️</div>
          <div>
            <h1>מאגרי נתונים</h1>
            <p>עיון וחיפוש בכלל מאגרי משרד הבריאות</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            f'<div style="font-size:0.85rem; color:{COLORS["text_muted"]}; margin-bottom:1rem">'
            f'מציג <b>{len(filtered):,}</b> מאגרים מתוך {len(df):,}'
            f'</div>',
            unsafe_allow_html=True,
        )

        if filtered.empty:
            st.info("לא נמצאו תוצאות לחיפוש זה.")
        else:
            for _, row in filtered.head(50).iterrows():
                url = f"https://data.gov.il/dataset/{row.get('name', '')}"
                fmt_badges = "".join(
                    f'<span class="badge badge-teal">{f.strip()}</span>'
                    for f in str(row.get("formats", "")).split(",")
                    if f.strip()
                )
                tags_badges = "".join(
                    f'<span class="badge badge-blue">{t.strip()}</span>'
                    for t in str(row.get("tags", "")).split(",")
                    if t.strip()
                )
                notes = row.get("notes", "") or ""
                st.markdown(f"""
                <div class="dataset-row">
                  <div class="dataset-title">
                    <a href="{url}" target="_blank"
                       style="color:{COLORS['primary']}; text-decoration:none;">
                      {row.get('title', row.get('name', ''))}
                    </a>
                  </div>
                  {f'<div style="font-size:0.8rem; color:{COLORS["text_muted"]}; margin: 0.3rem 0;">{notes[:110]}{"..." if len(notes) > 110 else ""}</div>' if notes else ''}
                  <div class="dataset-meta">
                    {fmt_badges} {tags_badges}
                    <span class="badge badge-blue">📁 {row.get('resources', 0)}</span>
                    <span style="color:{COLORS['text_muted']}; font-size:0.74rem; margin-right:0.5rem">
                      {row.get('modified', '—')}
                    </span>
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # ════════════════════════════════════════
    # PAGE: ניתוח
    # ════════════════════════════════════════
    elif page == "ניתוח":
        st.markdown("""
        <div class="moh-header">
          <div class="moh-logo">📈</div>
          <div>
            <h1>ניתוח נתונים</h1>
            <p>סטטיסטיקות ותובנות על מאגרי משרד הבריאות</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="medium")

        with col1:
            st.markdown(section_header("📦", "תגיות נפוצות"), unsafe_allow_html=True)
            if "tags" in df.columns:
                tag_counts = (
                    df["tags"]
                    .str.split(", ")
                    .explode()
                    .str.strip()
                    .replace("", pd.NA)
                    .dropna()
                    .value_counts()
                    .head(12)
                )
                fig = px.bar(
                    x=tag_counts.values,
                    y=tag_counts.index,
                    orientation="h",
                    color=tag_counts.values,
                    color_continuous_scale=[[0, COLORS["blue_light"]], [1, COLORS["primary"]]],
                )
                fig.update_layout(
                    height=380,
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    showlegend=False,
                    coloraxis_showscale=False,
                    yaxis=dict(showgrid=False),
                    xaxis=dict(showgrid=True, gridcolor="#EEF4FB"),
                    font=dict(family="Rubik, Arial", size=11, color=COLORS["text"]),
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(section_header("📁", "קבצים למאגר"), unsafe_allow_html=True)
            if "resources" in df.columns:
                res_dist = df["resources"].clip(upper=20).value_counts().sort_index()
                fig2 = go.Figure(go.Bar(
                    x=res_dist.index,
                    y=res_dist.values,
                    marker_color=COLORS["teal"],
                    opacity=0.85,
                ))
                fig2.update_layout(
                    height=380,
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    xaxis=dict(title="מספר קבצים", showgrid=False),
                    yaxis=dict(title="מאגרים", showgrid=True, gridcolor="#EEF4FB"),
                    font=dict(family="Rubik, Arial", size=12, color=COLORS["text"]),
                )
                st.plotly_chart(fig2, use_container_width=True)

        # Full table
        st.markdown(section_header("📋", "טבלה מלאה"), unsafe_allow_html=True)
        display_cols = [c for c in ["title", "formats", "resources", "tags", "modified"]
                        if c in filtered.columns]
        st.dataframe(
            filtered[display_cols].rename(columns={
                "title": "שם המאגר",
                "formats": "פורמטים",
                "resources": "קבצים",
                "tags": "תגיות",
                "modified": "עדכון אחרון",
            }),
            use_container_width=True,
            height=400,
            hide_index=True,
        )

    # ── FOOTER ──
    st.markdown("""
    <div class="moh-footer">
      <b>משרד הבריאות</b> · נתונים מתוך
      <a href="https://data.gov.il" target="_blank">data.gov.il</a>
      · רשות הנתונים הלאומית · כל הנתונים פתוחים לציבור
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
