"""
שליפת נתונים מ-data.gov.il - משרד הבריאות
"""

import requests
import pandas as pd
import json
import time
from pathlib import Path

BASE_URL = "https://data.gov.il/api/3/action"
ORG = "ministry-health"
RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def get_all_datasets(rows=1000):
    """שליפת רשימת כל מאגרי משרד הבריאות"""
    url = f"{BASE_URL}/package_search"
    params = {
        "fq": f"organization:{ORG}",
        "rows": rows,
        "start": 0,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    results = data["result"]["results"]
    total = data["result"]["count"]
    print(f"נמצאו {total} מאגרים")
    return results


def get_dataset_info(dataset_id):
    """פרטי מאגר ספציפי לפי ID"""
    url = f"{BASE_URL}/package_show"
    resp = requests.get(url, params={"id": dataset_id}, timeout=30)
    resp.raise_for_status()
    return resp.json()["result"]


def download_resource(resource_url, filename, delay=0.5):
    """הורדת קובץ נתונים מ-URL"""
    dest = RAW_DIR / filename
    if dest.exists():
        print(f"קיים כבר: {filename}")
        return dest

    time.sleep(delay)
    resp = requests.get(resource_url, timeout=60)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    print(f"הורד: {filename}")
    return dest


def list_datasets_as_dataframe():
    """מחזיר DataFrame עם כל המאגרים"""
    datasets = get_all_datasets()
    rows = []
    for ds in datasets:
        rows.append({
            "id": ds.get("id"),
            "name": ds.get("name"),
            "title": ds.get("title"),
            "notes": ds.get("notes", "")[:100],
            "num_resources": len(ds.get("resources", [])),
            "metadata_modified": ds.get("metadata_modified"),
        })
    df = pd.DataFrame(rows)
    df.to_csv(RAW_DIR / "datasets_list.csv", index=False, encoding="utf-8-sig")
    print(f"נשמר: datasets_list.csv")
    return df


if __name__ == "__main__":
    df = list_datasets_as_dataframe()
    print(df.head(20).to_string())
