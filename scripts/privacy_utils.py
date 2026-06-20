"""Shared helpers for privacy-risk experiment scripts."""

from __future__ import annotations

import os
from datetime import date

import pandas as pd


def monday_week_start(series: pd.Series) -> pd.Series:
    """Return canonical Monday-start week labels as YYYY-MM-DD strings."""

    dt = pd.to_datetime(series, errors="coerce")
    monday = dt.dt.normalize() - pd.to_timedelta(dt.dt.weekday, unit="D")
    return monday.dt.strftime("%Y-%m-%d").fillna("")


def report_date() -> str:
    """Return the local date used in regenerated Markdown summaries."""

    return os.environ.get("PROJECT_REPORT_DATE", date.today().isoformat())
