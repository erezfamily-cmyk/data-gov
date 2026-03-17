"""
מפה אינטראקטיבית של מרכזי חוסן - data.gov.il
עיצוב: מערכת עיצוב משרד הבריאות
"""

import requests
import time
import json
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

RESOURCE_ID = "457673b2-c3c4-4cb5-909c-03b29d8ce1ff"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
GEOCACHE_FILE = OUTPUT_DIR / "geocache.json"

MANUAL_COORDS = {
    "גוש עציון":     (31.657, 35.108),
    "מעלה אדומים":   (31.777, 35.293),
    "אדומים":        (31.777, 35.293),
    "אפרת":          (31.659, 35.162),
    "שומרון":        (32.188, 35.096),
    "קרני שומרון":   (32.167, 35.121),
    "כוכב יעקב":     (31.876, 35.241),
    "קרית ארבע":     (31.533, 35.114),
    "ארד":           (31.258, 35.213),
}

# צבעים מרוחניים ממערכת העיצוב של משרד הבריאות
COLORS = [
    "#1D8277", "#365CE9", "#A03C7A", "#388315", "#C0570A",
    "#C92D66", "#A154B6", "#017FA6", "#27665F", "#2D6A4F",
    "#F4A261", "#264653", "#6A4C93", "#8AC926", "#FB8500", "#219EBC",
]


# ─── API ──────────────────────────────────────────────────────────────────────

def fetch_centers():
    r = requests.get(
        "https://data.gov.il/api/3/action/datastore_search",
        params={"resource_id": RESOURCE_ID, "limit": 500},
        timeout=30,
    )
    r.raise_for_status()
    records = r.json()["result"]["records"]
    print(f"נשלפו {len(records)} מרכזי חוסן")
    return records


# ─── Geocoding ────────────────────────────────────────────────────────────────

def load_geocache():
    if GEOCACHE_FILE.exists():
        raw = json.loads(GEOCACHE_FILE.read_text(encoding="utf-8"))
        return {k: tuple(v) if v else None for k, v in raw.items()}
    return {}


def save_geocache(cache):
    GEOCACHE_FILE.write_text(
        json.dumps({k: list(v) if v else None for k, v in cache.items()},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def geocode(name, cache):
    if name in cache:
        return cache[name]
    if not name or not name.strip():
        return None
    for key, coords in MANUAL_COORDS.items():
        if key in name or name in key:
            cache[name] = coords
            return coords
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": f"{name}, Israel", "format": "json", "limit": 1},
            headers={"User-Agent": "data-gov-health-map/1.0"},
            timeout=10,
        )
        results = resp.json()
        if results:
            coords = (float(results[0]["lat"]), float(results[0]["lon"]))
            cache[name] = coords
            return coords
    except Exception as e:
        print(f"  שגיאה: '{name}': {e}")
    cache[name] = None
    return None


# ─── HTML Template ────────────────────────────────────────────────────────────

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>מרכזי חוסן - משרד הבריאות</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;700&display=swap" rel="stylesheet">
  {plotly_script}
  <style>
    :root {{
      --theme-100: #EBFAF8;
      --theme-200: #CEF2EE;
      --theme-300: #70CCC1;
      --theme-400: #1D8277;
      --theme-500: #27665F;
      --surface-100: #FFFFFF;
      --surface-200: #F8FAFE;
      --surface-300: #F0F4FC;
      --surface-400: #DDDFE4;
      --surface-500: #BCBEC2;
      --text-300: #8991AC;
      --text-400: #5E6783;
      --text-500: #394159;
      --text-600: #1B2030;
      --shadow-card: 0 1px 12px rgba(87,84,84,0.13);
      --shadow-hover: 0px 4px 8px rgba(27,32,48,0.12);
      --radius: 16px;
    }}

    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: 'Rubik', sans-serif;
      background: var(--surface-200);
      color: var(--text-500);
      direction: rtl;
      font-size: 16px;
      line-height: 1.5;
    }}

    /* ── Header ── */
    .moh-header {{
      background: var(--surface-100);
      border-bottom: 1px solid var(--surface-400);
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .header-inner {{
      max-width: 1318px;
      margin: 0 auto;
      padding: 0 48px;
      height: 80px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .logo-block {{
      display: flex;
      align-items: center;
      gap: 14px;
      text-decoration: none;
    }}
    .logo-emblem {{
      width: 48px;
      height: 48px;
      background: var(--theme-400);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}
    .logo-emblem svg {{ width: 28px; height: 28px; fill: white; }}
    .logo-text {{ border-right: 1px solid var(--surface-400); padding-right: 14px; }}
    .logo-text .gov  {{ font-size: 11px; color: var(--text-400); letter-spacing: 0.04em; }}
    .logo-text .dept {{ font-size: 15px; font-weight: 700; color: var(--text-600); }}
    .header-badge {{
      background: var(--theme-100);
      color: var(--theme-500);
      font-size: 13px;
      font-weight: 500;
      padding: 6px 16px;
      border-radius: 20px;
      border: 1px solid var(--theme-200);
    }}
    .header-teal-bar {{
      height: 5px;
      background: linear-gradient(90deg, var(--theme-400) 0%, var(--theme-300) 100%);
    }}

    /* ── Hero ── */
    .hero {{
      background: linear-gradient(135deg, var(--theme-500) 0%, var(--theme-400) 60%, var(--theme-300) 100%);
      color: white;
      padding: 56px 48px 48px;
      text-align: center;
    }}
    .hero h1 {{
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 12px;
      letter-spacing: -0.01em;
    }}
    .hero p {{
      font-size: 1.1rem;
      opacity: 0.88;
      max-width: 560px;
      margin: 0 auto 36px;
    }}
    .stats-row {{
      display: flex;
      justify-content: center;
      gap: 24px;
      flex-wrap: wrap;
    }}
    .stat-card {{
      background: rgba(255,255,255,0.15);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255,255,255,0.3);
      border-radius: var(--radius);
      padding: 20px 32px;
      min-width: 140px;
    }}
    .stat-num {{
      font-size: 2rem;
      font-weight: 700;
      display: block;
      margin-bottom: 4px;
    }}
    .stat-label {{
      font-size: 0.85rem;
      opacity: 0.85;
    }}

    /* ── Map Section ── */
    .map-section {{
      max-width: 1318px;
      margin: 0 auto;
      padding: 40px 48px 0;
    }}
    .section-title {{
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--text-600);
      margin-bottom: 8px;
    }}
    .section-sub {{
      font-size: 0.95rem;
      color: var(--text-400);
      margin-bottom: 24px;
    }}
    .map-wrapper {{
      border-radius: var(--radius);
      overflow: hidden;
      box-shadow: var(--shadow-card);
      border: 1px solid var(--surface-400);
      background: white;
    }}

    /* ── Legend pills ── */
    .legend-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      padding: 16px 20px;
      border-top: 1px solid var(--surface-300);
      background: var(--surface-100);
    }}
    .legend-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      border: 1.5px solid;
      cursor: pointer;
      transition: opacity 0.2s;
    }}
    .legend-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      flex-shrink: 0;
    }}

    /* ── Centers Cards ── */
    .cards-section {{
      max-width: 1318px;
      margin: 0 auto;
      padding: 40px 48px 64px;
    }}
    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 24px;
    }}
    .center-card {{
      background: var(--surface-100);
      border: 1px solid var(--surface-400);
      border-radius: var(--radius);
      overflow: hidden;
      box-shadow: var(--shadow-card);
      transition: box-shadow 0.3s, border-color 0.3s;
      display: flex;
      flex-direction: column;
    }}
    .center-card:hover {{
      box-shadow: var(--shadow-hover);
      border-color: var(--theme-300);
    }}
    .card-header-bar {{
      height: 6px;
    }}
    .card-body {{
      padding: 24px;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .card-name {{
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--text-600);
    }}
    .card-city {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 0.85rem;
      color: var(--theme-500);
      font-weight: 500;
      background: var(--theme-100);
      padding: 3px 10px;
      border-radius: 12px;
      width: fit-content;
    }}
    .card-address {{
      font-size: 0.88rem;
      color: var(--text-400);
      display: flex;
      align-items: flex-start;
      gap: 6px;
    }}
    .card-row {{
      font-size: 0.88rem;
      color: var(--text-500);
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .card-row a {{
      color: var(--theme-500);
      text-decoration: none;
    }}
    .card-row a:hover {{ text-decoration: underline; }}
    .card-coverage {{
      margin-top: auto;
      padding-top: 12px;
      border-top: 1px solid var(--surface-300);
      font-size: 0.82rem;
      color: var(--text-400);
    }}
    .coverage-tag {{
      display: inline-block;
      background: var(--surface-300);
      border-radius: 8px;
      padding: 2px 8px;
      margin: 2px;
      font-size: 0.78rem;
      color: var(--text-500);
    }}

    /* ── Footer ── */
    .moh-footer {{
      background: var(--text-600);
      color: rgba(255,255,255,0.7);
      text-align: center;
      padding: 28px 48px;
      font-size: 0.85rem;
    }}
    .moh-footer a {{
      color: var(--theme-300);
      text-decoration: none;
    }}
    .moh-footer a:hover {{ text-decoration: underline; }}

    @media (max-width: 768px) {{
      .header-inner {{ padding: 0 20px; height: 60px; }}
      .hero {{ padding: 36px 20px 32px; }}
      .hero h1 {{ font-size: 1.8rem; }}
      .map-section, .cards-section {{ padding-inline: 16px; }}
      .stat-card {{ padding: 16px 20px; min-width: 110px; }}
    }}
  </style>
</head>
<body>

<!-- ── Header ── -->
<header class="moh-header">
  <div class="header-inner">
    <div class="logo-block">
      <div class="logo-emblem">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/>
        </svg>
      </div>
      <div class="logo-text">
        <div class="gov">מדינת ישראל</div>
        <div class="dept">משרד הבריאות</div>
      </div>
    </div>
    <span class="header-badge">מרכזי חוסן</span>
  </div>
  <div class="header-teal-bar"></div>
</header>

<!-- ── Hero ── -->
<section class="hero">
  <h1>מרכזי חוסן בישראל</h1>
  <p>מרכזי התמיכה הקהילתיים של משרד הבריאות — עזרה נפשית ורגשית לפרטים ולמשפחות</p>
  <div class="stats-row">
    <div class="stat-card">
      <span class="stat-num">{num_centers}</span>
      <span class="stat-label">מרכזי חוסן</span>
    </div>
    <div class="stat-card">
      <span class="stat-num">{num_coverage}</span>
      <span class="stat-label">ערים בכיסוי</span>
    </div>
    <div class="stat-card">
      <span class="stat-num">*5486</span>
      <span class="stat-label">קו חירום</span>
    </div>
  </div>
</section>

<!-- ── Map ── -->
<section class="map-section">
  <h2 class="section-title">מפת מרכזי החוסן</h2>
  <p class="section-sub">לחצו על נקודה במפה לפרטי המרכז. נקודות קטנות — ערים בתחום הכיסוי.</p>
  <div class="map-wrapper">
    {plotly_div}
    <div class="legend-row">
      {legend_pills}
    </div>
  </div>
</section>

<!-- ── Cards ── -->
<section class="cards-section">
  <h2 class="section-title">פרטי המרכזים</h2>
  <p class="section-sub">מידע יצירת קשר ואזורי שירות לכל מרכז חוסן</p>
  <div class="cards-grid">
    {cards_html}
  </div>
</section>

<!-- ── Footer ── -->
<footer class="moh-footer">
  <p>
    נתונים: <a href="https://data.gov.il" target="_blank">data.gov.il</a> &nbsp;|&nbsp;
    מאגר: <a href="https://data.gov.il/dataset/resilience-centers" target="_blank">מרכזי חוסן</a> &nbsp;|&nbsp;
    &copy; משרד הבריאות
  </p>
</footer>

</body>
</html>
"""


def build_center_card(center, cov_count, color):
    phone = center["phone"]
    if center["phone2"]:
        phone += f" / {center['phone2']}"

    other_raw = center.get("other_cities_raw", "")
    cities = [c.strip() for c in other_raw.replace("،", ",").split(",") if c.strip()]
    city_tags = "".join(f'<span class="coverage-tag">{c}</span>' for c in cities[:12])
    more = f'<span class="coverage-tag">+{len(cities)-12} נוספות</span>' if len(cities) > 12 else ""

    phone_html = f'<div class="card-row"><span>&#128222;</span> {phone}</div>' if phone else ""
    email_html = (
        f'<div class="card-row"><span>&#9993;</span> <a href="mailto:{center["email"]}">{center["email"]}</a></div>'
        if center["email"] else ""
    )
    address_html = (
        f'<div class="card-address"><span>&#128205;</span> {center["address"]}</div>'
        if center["address"] and center["address"] != center["city"] else ""
    )
    coverage_html = (
        f'<div class="card-coverage">{city_tags}{more}</div>'
        if cities else ""
    )

    return f"""
    <div class="center-card">
      <div class="card-header-bar" style="background:{color}"></div>
      <div class="card-body">
        <div class="card-name">{center["name"]}</div>
        <div class="card-city"><span>&#127968;</span>{center["city"]}</div>
        {address_html}
        {phone_html}
        {email_html}
        {coverage_html}
      </div>
    </div>"""


def build_map(records):
    geocache = load_geocache()
    print(f"מטמון גיאוקודינג: {len(geocache)} ערים")
    centers = []

    # שלב 1: גיאוקודינג מרכזים
    print("\n=== גיאוקודינג מרכזים ===")
    for i, rec in enumerate(records):
        city = rec.get("city", "").strip()
        name = rec.get("institute_name", "").strip()
        if not city:
            continue
        print(f"  [{i+1}] {city}...")
        coords = geocode(city, geocache)
        if i > 0 and city not in geocache:
            time.sleep(1.1)
        if not coords:
            print(f"      נכשל!")
            continue
        centers.append({
            "id": rec["_id"],
            "name": name,
            "city": city,
            "address": rec.get("address", "").strip() or city,
            "phone": rec.get("phone", "").strip(),
            "phone2": rec.get("phone2", "").strip(),
            "email": rec.get("email", "").strip(),
            "other_cities_raw": rec.get("other_cities", "").strip(),
            "notes": rec.get("el_notes", "").strip(),
            "lat": coords[0],
            "lon": coords[1],
            "color": COLORS[i % len(COLORS)],
        })
    save_geocache(geocache)
    print(f"מרכזים שנמצאו: {len(centers)}")

    # שלב 2: גיאוקודינג ערים נוספות
    print("\n=== גיאוקודינג ערים נוספות ===")
    coverage_rows = []
    for center in centers:
        raw = center["other_cities_raw"]
        if not raw:
            continue
        city_list = [c.strip() for c in raw.replace("،", ",").split(",") if c.strip()]
        print(f"  {center['city']}: {len(city_list)} ערים")
        for c in city_list:
            needs_sleep = c not in geocache
            coords = geocode(c, geocache)
            if coords:
                coverage_rows.append({
                    "city": c,
                    "center_id": center["id"],
                    "center_name": center["name"],
                    "center_city": center["city"],
                    "lat": coords[0],
                    "lon": coords[1],
                    "color": center["color"],
                })
            if needs_sleep:
                time.sleep(1.1)
    save_geocache(geocache)
    print(f"ערים נוספות שנמצאו: {len(coverage_rows)}")

    # שלב 3: בניית Plotly figure
    fig = go.Figure()

    for center in centers:
        cov = [r for r in coverage_rows if r["center_id"] == center["id"]]
        if cov:
            fig.add_trace(go.Scattermap(
                lat=[r["lat"] for r in cov],
                lon=[r["lon"] for r in cov],
                mode="markers",
                marker=dict(size=7, color=center["color"], opacity=0.35),
                name=f"כיסוי: {center['city']}",
                legendgroup=f"c{center['id']}",
                showlegend=False,
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    f"מרכז: {center['name']}<extra></extra>"
                ),
                text=[r["city"] for r in cov],
            ))

    for center in centers:
        phone = center["phone"]
        if center["phone2"]:
            phone += f" / {center['phone2']}"
        cov_count = sum(1 for r in coverage_rows if r["center_id"] == center["id"])
        hover = f"<b>{center['name']}</b><br>&#128205; {center['address']}<br>"
        if phone:
            hover += f"&#128222; {phone}<br>"
        if center["email"]:
            hover += f"&#9993; {center['email']}<br>"
        if cov_count:
            hover += f"&#127968; מכסה {cov_count} ערים נוספות"

        fig.add_trace(go.Scattermap(
            lat=[center["lat"]],
            lon=[center["lon"]],
            mode="markers+text",
            marker=dict(size=16, color=center["color"], opacity=0.95),
            text=[center["city"]],
            textposition="top center",
            textfont=dict(size=11, color="#1B2030", family="Rubik, sans-serif"),
            name=center["name"],
            legendgroup=f"c{center['id']}",
            showlegend=False,
            hovertemplate=hover + "<extra></extra>",
        ))

    fig.update_layout(
        map=dict(
            style="open-street-map",
            center=dict(lat=31.6, lon=34.9),
            zoom=6.8,
        ),
        height=600,
        margin=dict(r=0, t=0, l=0, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
    )

    # נשלוף את ה-script tag של plotly בנפרד מה-div
    full_html = fig.to_html(full_html=False, include_plotlyjs="cdn", config={
        "displaylogo": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "responsive": True,
    })
    # הפרד script מה-div
    import re as _re
    script_match = _re.search(r'(<script[^>]*src=[^>]*plotly[^>]*></script>)', full_html)
    plotly_script = script_match.group(1) if script_match else ""
    plotly_div = _re.sub(r'<script[^>]*src=[^>]*plotly[^>]*></script>', "", full_html).strip()

    # שלב 4: בניית HTML
    legend_pills = ""
    for center in centers:
        cov_count = sum(1 for r in coverage_rows if r["center_id"] == center["id"])
        legend_pills += (
            f'<span class="legend-pill" style="color:{center["color"]};'
            f'border-color:{center["color"]};background:white">'
            f'<span class="legend-dot" style="background:{center["color"]}"></span>'
            f'{center["name"]}'
            f'</span>'
        )

    cards_html = ""
    for center in centers:
        cov_count = sum(1 for r in coverage_rows if r["center_id"] == center["id"])
        cards_html += build_center_card(center, cov_count, center["color"])

    html = HTML_TEMPLATE.format(
        num_centers=len(centers),
        num_coverage=len(coverage_rows),
        plotly_script=plotly_script,
        plotly_div=plotly_div,
        legend_pills=legend_pills,
        cards_html=cards_html,
    )

    out_path = OUTPUT_DIR / "resilience_centers_map.html"
    out_path.write_text(html, encoding="utf-8")

    pd.DataFrame(centers).to_csv(
        OUTPUT_DIR / "resilience_centers_geo.csv", index=False, encoding="utf-8-sig"
    )
    pd.DataFrame(coverage_rows).to_csv(
        OUTPUT_DIR / "resilience_coverage.csv", index=False, encoding="utf-8-sig"
    )

    print(f"נשמרה מפה: {out_path}")
    print(f"{len(centers)} מרכזים, {len(coverage_rows)} ערים כיסוי")
    return str(out_path)


if __name__ == "__main__":
    records = fetch_centers()
    build_map(records)
