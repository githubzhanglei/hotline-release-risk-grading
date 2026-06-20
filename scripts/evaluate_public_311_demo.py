"""Aggregate-only public 311 structural-risk demo.

This script fetches a small fixed-window sample from the public NYC 311 API,
normalizes a few common Open311-style fields, and computes the same style of
structural grouping metrics used by the municipal-service release workflow.

No raw 311 rows, addresses, or row-level candidate lists are written. The output
contains aggregate metrics only.
"""

from __future__ import annotations

import argparse
import json
import math
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd


NYC_311_ENDPOINT = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
DEFAULT_OUTPUT_DIR = Path("example_outputs")
DEFAULT_START = "2024-02-01T00:00:00"
DEFAULT_END = "2024-02-08T00:00:00"
DEFAULT_LIMIT = 1000

NYC_FIELDS = [
    "created_date",
    "agency",
    "complaint_type",
    "descriptor",
    "incident_zip",
    "borough",
    "incident_address",
    "status",
]

SCENARIOS = [
    ("citywide", []),
    ("borough_week_type", ["borough", "week_start", "complaint_type"]),
    ("zip_week_type", ["incident_zip", "week_start", "complaint_type"]),
    ("zip_week_type_status", ["incident_zip", "week_start", "complaint_type", "status"]),
    (
        "zip_day_type_descriptor",
        ["incident_zip", "day", "complaint_type", "descriptor"],
    ),
    (
        "relation_key_released",
        ["incident_zip", "week_start", "complaint_type", "location_key"],
    ),
]


def fetch_nyc_311(start: str, end: str, limit: int) -> tuple[pd.DataFrame, str]:
    where = f"created_date between '{start}' and '{end}' AND incident_address IS NOT NULL"
    params = {
        "$limit": str(limit),
        "$select": ",".join(NYC_FIELDS),
        "$where": where,
        "$order": "created_date ASC",
    }
    url = NYC_311_ENDPOINT + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "hotline-release-risk-grading/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return pd.DataFrame(payload), url


def monday_week_start(values: pd.Series) -> pd.Series:
    return (values - pd.to_timedelta(values.dt.weekday, unit="D")).dt.date.astype(str)


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in NYC_FIELDS:
        if col not in out.columns:
            out[col] = ""
    for col in NYC_FIELDS:
        out[col] = out[col].fillna("").astype(str).str.strip()
    out["created_dt"] = pd.to_datetime(out["created_date"], errors="coerce")
    out = out[out["created_dt"].notna()].copy()
    out["day"] = out["created_dt"].dt.date.astype(str)
    out["week_start"] = monday_week_start(out["created_dt"])
    out["location_key"] = out["incident_address"].str.upper().str.replace(r"\s+", " ", regex=True)
    return out[out["location_key"].ne("")].copy()


def make_key(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    if not cols:
        return pd.Series(["<GLOBAL>"] * len(df), index=df.index)
    frame = df[cols].fillna("").replace("", "<MISSING>").astype(str)
    key = frame.iloc[:, 0].copy()
    for col in frame.columns[1:]:
        key = key + " || " + frame[col]
    return key


def entropy_bits(values: pd.Series) -> float:
    counts = values.value_counts(dropna=False)
    total = float(counts.sum())
    if total <= 0:
        return 0.0
    probs = counts / total
    return float(-(probs * probs.map(math.log2)).sum())


def evaluate(df: pd.DataFrame, label: str, cols: list[str]) -> dict[str, object]:
    if df.empty:
        return {
            "city": "NYC",
            "scenario": label,
            "qid_columns": " + ".join(cols) if cols else "<none>",
            "records": 0,
            "target_locations": 0,
            "qid_groups": 0,
            "pct_records_k1": 0.0,
            "median_k_records": 0.0,
            "map_location_linkage": 0.0,
            "h_location_bits": 0.0,
            "h_location_given_q_bits": 0.0,
            "i_struct_location_bits": 0.0,
            "effective_location_candidates": 0.0,
        }

    keys = make_key(df, cols)
    work = df.copy()
    work["_qid_key"] = keys
    group_sizes = keys.map(keys.value_counts())

    h_location = entropy_bits(work["location_key"])
    h_location_given_q = 0.0
    for _, group in work.groupby("_qid_key", sort=False):
        h_location_given_q += (len(group) / len(work)) * entropy_bits(group["location_key"])
    i_struct = max(0.0, h_location - h_location_given_q)

    max_counts = work.groupby("_qid_key")["location_key"].value_counts().groupby(level=0).max()
    map_linkage = float(max_counts.sum() / len(work))

    return {
        "city": "NYC",
        "scenario": label,
        "qid_columns": " + ".join(cols) if cols else "<none>",
        "records": int(len(work)),
        "target_locations": int(work["location_key"].nunique()),
        "qid_groups": int(keys.nunique()),
        "pct_records_k1": float((group_sizes == 1).mean()),
        "median_k_records": float(group_sizes.median()),
        "map_location_linkage": map_linkage,
        "h_location_bits": h_location,
        "h_location_given_q_bits": h_location_given_q,
        "i_struct_location_bits": i_struct,
        "effective_location_candidates": float(2**h_location_given_q),
    }


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def write_summary(results: pd.DataFrame, output_dir: Path, source_url: str, start: str, end: str) -> None:
    lines = [
        "# Public 311 Structural Demo Summary",
        "",
        "Source: NYC 311 public API.",
        f"Window: `{start}` to `{end}`.",
        "",
        "The script writes aggregate metrics only. It does not save raw 311 rows, addresses, or row-level candidate lists.",
        "",
        "| Scenario | Records | Locations | k=1 uniqueness | MAP location linkage | Effective location candidates |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in results.iterrows():
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["scenario"]),
                    str(int(row["records"])),
                    str(int(row["target_locations"])),
                    pct(float(row["pct_records_k1"])),
                    pct(float(row["map_location_linkage"])),
                    f"{float(row['effective_location_candidates']):.2f}",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Source query URL is stored for provenance but no source rows are stored.",
            "",
            f"`{source_url}`",
        ]
    )
    (output_dir / "public_311_nyc_structural_demo_summary.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--end", default=DEFAULT_END)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    args = parser.parse_args()

    raw, source_url = fetch_nyc_311(args.start, args.end, args.limit)
    df = normalize(raw)
    rows = [evaluate(df, label, cols) for label, cols in SCENARIOS]
    results = pd.DataFrame(rows)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(
        args.output_dir / "public_311_nyc_structural_demo.csv",
        index=False,
        encoding="utf-8-sig",
    )
    write_summary(results, args.output_dir, source_url, args.start, args.end)
    print(f"Wrote public 311 aggregate demo outputs to {args.output_dir}")


if __name__ == "__main__":
    main()
