# data-gov - מאגר נתוני בריאות ישראלי

## סקירת הפרויקט
פרויקט לשליפה, עיבוד וניתוח נתוני משרד הבריאות מפורטל הנתונים הפתוחים של ממשלת ישראל (data.gov.il).

## מקור הנתונים
- **פורטל:** https://data.gov.il
- **API:** CKAN API v3 - `https://data.gov.il/api/3/action/`
- **ארגון:** משרד הבריאות (`ministry-of-health`)
- **תיעוד API:** https://docs.ckan.org/en/2.9/api/

## מטרות הפרויקט
1. שליפת כל מאגרי משרד הבריאות מה-API
2. ניתוח וסטטיסטיקות (מי חולה במה, איפה, מתי)
3. ויזואליזציה - גרפים ומפות אינטראקטיביות
4. דשבורד אינטראקטיבי לצפייה שוטפת
5. עיבוד/ניקוי נתונים ושמירה למאגר מקומי (SQLite)

## Stack טכנולוגי
- **Python 3.x**
- `requests` - שליפת נתונים מה-API
- `pandas` - עיבוד וניתוח נתונים
- `plotly` - גרפים ומפות אינטראקטיביות
- `streamlit` - דשבורד web
- `sqlite3` - מאגר נתונים מקומי (מובנה ב-Python)

## מבנה הפרויקט
```
data-gov/
├── CLAUDE.md              # קובץ זה
├── requirements.txt       # תלויות Python
├── src/
│   ├── fetch.py           # שליפת נתונים מה-API
│   ├── process.py         # עיבוד וניקוי נתונים
│   ├── analyze.py         # ניתוח וסטטיסטיקות
│   ├── visualize.py       # גרפים ומפות
│   └── db.py              # עבודה עם SQLite
├── dashboard/
│   └── app.py             # Streamlit dashboard
├── data/
│   ├── raw/               # נתונים גולמיים מה-API
│   ├── processed/         # נתונים מעובדים
│   └── health.db          # מאגר SQLite
└── notebooks/             # ניתוחים חד-פעמיים
```

## API - דוגמאות שימוש
```python
# חיפוש כל מאגרי משרד הבריאות
GET https://data.gov.il/api/3/action/package_search?q=organization:ministry-of-health&rows=100

# פרטי מאגר ספציפי
GET https://data.gov.il/api/3/action/package_show?id=<dataset-id>

# הורדת קובץ
GET https://data.gov.il/dataset/<dataset-id>/resource/<resource-id>/download/<filename>
```

## הערות
- הנתונים פתוחים לציבור - אין צורך ב-API key
- חלק מהקבצים בעברית - יש לוודא קידוד UTF-8
- כדאי להוסיף rate limiting בין קריאות API
