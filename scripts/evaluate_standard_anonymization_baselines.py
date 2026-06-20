"""Evaluate standard anonymization ladder baselines.

This script adds conventional data-anonymization comparators for the cybersec
paper: geographic/time/topic recoding and row-level k-anonymity suppression.
It is intentionally conservative and aggregate-only.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import entropy as scipy_entropy

from privacy_utils import monday_week_start, report_date


DEFAULT_INPUT = Path("data_sample/synthetic_hotline_sample.csv")
DEFAULT_OUTPUT_DIR = Path("example_outputs")

DISTRICT = "\u533a\u53bf\u5730\u5740"
STREET = "\u8857\u9053\u5730\u5740"
SOLVED = "\u95ee\u9898\u662f\u5426\u89e3\u51b3"


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ticket_dt"] = pd.to_datetime(out["ticket_date"], errors="coerce")
    out["week_start"] = monday_week_start(out["ticket_dt"])
    out["month_start"] = out["ticket_dt"].dt.to_period("M").apply(
        lambda p: "" if pd.isna(p) else str(p.start_time.date())
    )
    for col in out.columns:
        if out[col].dtype == object:
            out[col] = out[col].fillna("").astype(str).str.strip()
    return out


def shannon_entropy_bits(values: pd.Series) -> float:
    counts = values.value_counts(dropna=False).to_numpy(dtype=float)
    if counts.sum() == 0:
        return 0.0
    probs = counts / counts.sum()
    return float(scipy_entropy(probs, base=2))


def fano_error_lower_bound_bits(mutual_info_bits: float, num_classes: int) -> float:
    if num_classes <= 1:
        return 0.0
    return max(0.0, 1.0 - ((mutual_info_bits + 1.0) / math.log2(num_classes)))


def make_key(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    cols = [col for col in cols if col in df.columns]
    if not cols:
        return pd.Series(["<GLOBAL>"] * len(df), index=df.index)
    frame = df[cols].fillna("").replace("", "<MISSING>").astype(str)
    key = frame.iloc[:, 0].copy()
    for col in frame.columns[1:]:
        key = key + " || " + frame[col]
    return key


def evaluate_qid_combo(df: pd.DataFrame, label: str, cols: list[str]) -> dict[str, object]:
    person_df = df[df["person_id"].fillna("").ne("")].copy()
    cols = [col for col in cols if col in person_df.columns]
    if person_df.empty:
        return {
            "policy": label,
            "qid_columns": " + ".join(cols),
            "records_with_person": 0,
            "unique_persons": 0,
            "qid_groups": 0,
            "median_k_records": 0.0,
            "mean_k_records": 0.0,
            "pct_records_k1": 0.0,
            "pct_records_k_le_5": 0.0,
            "pct_records_k_le_10": 0.0,
            "median_person_l_diversity": 0.0,
            "mean_person_l_diversity": 0.0,
            "pct_records_person_l1": 0.0,
            "h_person_bits": 0.0,
            "h_person_given_q_bits": 0.0,
            "i_struct_empirical_bits": 0.0,
            "effective_person_candidates": 0.0,
            "map_reid_accuracy": 0.0,
            "random_within_qid_accuracy": 0.0,
            "fano_error_lb_uniform": 0.0,
        }
    keys = make_key(person_df, cols)
    person_df["_qid_key"] = keys

    group_sizes = keys.map(keys.value_counts())
    group_person_counts = person_df.groupby("_qid_key")["person_id"].nunique()
    record_person_l = keys.map(group_person_counts)

    h_person = shannon_entropy_bits(person_df["person_id"])
    h_person_given_q = 0.0
    for _, group in person_df.groupby("_qid_key", sort=False):
        weight = len(group) / len(person_df)
        h_person_given_q += weight * shannon_entropy_bits(group["person_id"])
    mi_bits = max(0.0, h_person - h_person_given_q)
    num_persons = int(person_df["person_id"].nunique())

    max_counts = person_df.groupby("_qid_key")["person_id"].value_counts().groupby(level=0).max()
    map_accuracy = float(max_counts.sum() / len(person_df))

    return {
        "policy": label,
        "qid_columns": " + ".join(cols) if cols else "<none>",
        "records_with_person": int(len(person_df)),
        "unique_persons": num_persons,
        "qid_groups": int(keys.nunique()),
        "median_k_records": float(group_sizes.median()),
        "mean_k_records": float(group_sizes.mean()),
        "pct_records_k1": float((group_sizes == 1).mean()),
        "pct_records_k_le_5": float((group_sizes <= 5).mean()),
        "pct_records_k_le_10": float((group_sizes <= 10).mean()),
        "median_person_l_diversity": float(record_person_l.median()),
        "mean_person_l_diversity": float(record_person_l.mean()),
        "pct_records_person_l1": float((record_person_l == 1).mean()),
        "h_person_bits": h_person,
        "h_person_given_q_bits": h_person_given_q,
        "i_struct_empirical_bits": mi_bits,
        "effective_person_candidates": float(2**h_person_given_q),
        "map_reid_accuracy": map_accuracy,
        "random_within_qid_accuracy": float((1.0 / record_person_l.replace(0, np.nan)).mean()),
        "fano_error_lb_uniform": fano_error_lower_bound_bits(mi_bits, num_persons),
    }


def risk_band(map_accuracy: float, k1: float) -> str:
    if map_accuracy <= 0.30 and k1 <= 0.15:
        return "low-to-moderate"
    if map_accuracy <= 0.40 and k1 <= 0.25:
        return "moderate"
    if map_accuracy <= 0.60 and k1 <= 0.45:
        return "high"
    return "critical"


def pct(value: float) -> float:
    return float(value) * 100.0


def detail_retention(df: pd.DataFrame, retained_mask: pd.Series, cols: list[str]) -> dict[str, float]:
    has_address = "address_id" in cols
    has_place = "text_place_id" in cols
    address_nonempty = df["address_id"].fillna("").astype(str).str.strip().ne("")
    place_nonempty = df["text_place_id"].fillna("").astype(str).str.strip().ne("")
    address_retained = float((retained_mask & address_nonempty).mean()) if has_address else 0.0
    place_retained = float((retained_mask & place_nonempty).mean()) if has_place else 0.0
    return {
        "address_detail_retained_pct": pct(address_retained),
        "text_place_detail_retained_pct": pct(place_retained),
        "relation_key_detail_retained_proxy_pct": pct(np.mean([address_retained, place_retained])),
    }


def retained_by_person_k(df: pd.DataFrame, cols: list[str], threshold: int) -> pd.Series:
    person_df = df[df["person_id"].fillna("").ne("")].copy()
    keys = make_key(person_df, cols)
    person_df["_qid_key"] = keys
    diversity = person_df.groupby("_qid_key")["person_id"].nunique()
    safe = set(diversity[diversity >= threshold].index)
    all_keys = make_key(df, cols)
    return all_keys.isin(safe)


def build_ladder(df: pd.DataFrame, thresholds: list[int]) -> pd.DataFrame:
    policy_specs = [
        ("global", "recoding", []),
        ("district_month_l1", "recoding", [DISTRICT, "month_start", "mapped_l1_name"]),
        ("district_week_l1", "recoding", [DISTRICT, "week_start", "mapped_l1_name"]),
        ("street_month_l1", "recoding", [DISTRICT, STREET, "month_start", "mapped_l1_name"]),
        ("street_month_l2", "recoding", [DISTRICT, STREET, "month_start", "mapped_l2_name"]),
        ("street_week_l1", "recoding", [DISTRICT, STREET, "week_start", "mapped_l1_name"]),
        ("street_week_l2", "recoding", [DISTRICT, STREET, "week_start", "mapped_l2_name"]),
        ("street_week_l2_solved", "recoding", [DISTRICT, STREET, "week_start", "mapped_l2_name", SOLVED]),
        (
            "street_week_l2_presence_flags",
            "coarse_relation_generalization",
            [DISTRICT, STREET, "week_start", "mapped_l2_name", "has_address_id", "has_text_place_id"],
        ),
        (
            "street_week_l2_place_type",
            "coarse_relation_generalization",
            [DISTRICT, STREET, "week_start", "mapped_l2_name", "text_place_type"],
        ),
        (
            "street_week_l2_raw_relation_keys",
            "unsafe_raw_relation_keys",
            [DISTRICT, STREET, "week_start", "mapped_l2_name", "address_id", "text_place_id"],
        ),
    ]
    rows: list[dict[str, object]] = []
    total_person_records = int(df["person_id"].fillna("").ne("").sum())
    all_retained = pd.Series(True, index=df.index)
    for policy, family, cols in policy_specs:
        row = evaluate_qid_combo(df, policy, cols)
        row.update(
            {
                "family": family,
                "suppression_threshold_persons": 0,
                "retained_all_records_pct": 100.0,
                "retained_person_records_pct": 100.0,
                "risk_band": risk_band(float(row["map_reid_accuracy"]), float(row["pct_records_k1"])),
            }
        )
        row.update(detail_retention(df, all_retained, cols))
        rows.append(row)

    suppression_specs = [
        ("topic_qid_row_suppression", [DISTRICT, STREET, "week_start", "mapped_l2_name"]),
        (
            "raw_relation_qid_row_suppression",
            [DISTRICT, STREET, "week_start", "mapped_l2_name", "address_id", "text_place_id"],
        ),
        (
            "presence_flag_qid_row_suppression",
            [DISTRICT, STREET, "week_start", "mapped_l2_name", "has_address_id", "has_text_place_id"],
        ),
    ]
    for name, cols in suppression_specs:
        for threshold in thresholds:
            retained = retained_by_person_k(df, cols, threshold)
            released_df = df[retained].copy()
            row = evaluate_qid_combo(released_df, f"{name}_k{threshold}", cols)
            retained_person_records = int(released_df["person_id"].fillna("").ne("").sum())
            row.update(
                {
                    "family": "standard_k_anonymity_row_suppression",
                    "suppression_threshold_persons": threshold,
                    "retained_all_records_pct": pct(float(retained.mean())),
                    "retained_person_records_pct": pct(
                        retained_person_records / total_person_records if total_person_records else 0.0
                    ),
                    "risk_band": risk_band(float(row["map_reid_accuracy"]), float(row["pct_records_k1"])),
                }
            )
            row.update(detail_retention(df, retained, cols))
            rows.append(row)
    return pd.DataFrame(rows)


def to_markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in df.iterrows():
        values = []
        for col in cols:
            value = row[col]
            if isinstance(value, float):
                values.append("" if pd.isna(value) else f"{value:.3f}")
            else:
                values.append(str(value).replace("\n", " "))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_summary(ladder: pd.DataFrame, output_dir: Path) -> None:
    path = output_dir / "standard_anonymization_ladder_summary.md"
    display_cols = [
        "policy",
        "family",
        "suppression_threshold_persons",
        "retained_person_records_pct",
        "pct_records_k1",
        "map_reid_accuracy",
        "fano_error_lb_uniform",
        "relation_key_detail_retained_proxy_pct",
        "risk_band",
    ]
    display = ladder[display_cols].copy()
    for col in ["pct_records_k1", "map_reid_accuracy", "fano_error_lb_uniform"]:
        display[col] = display[col].map(pct)

    lines = [
        "# Standard Anonymization Ladder Baselines",
        "",
        f"Date: {report_date()}",
        "",
        "Purpose: compare the relation-key controls against conventional recoding and k-anonymity-style row suppression baselines.",
        "Row suppression metrics are evaluated only on retained person records; utility must therefore be read together with retained record percentage.",
        "",
        "## Results",
        "",
        to_markdown_table(display),
        "",
        "## Interpretation",
        "",
        "- Coarse recoding lowers linkage risk by reducing geography, time, or topic precision, but also removes much of the monitoring value.",
        "- Standard row suppression can make the retained table safer, but may retain very few records when raw relation keys are included.",
        "- These baselines should be used to avoid claiming that topic-only is the only comparator.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--thresholds", type=int, nargs="+", default=[2, 5, 10, 20, 50])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    df = normalize_columns(pd.read_csv(args.input))
    ladder = build_ladder(df, args.thresholds)
    out_path = args.output_dir / "standard_anonymization_ladder.csv"
    ladder.to_csv(out_path, index=False, encoding="utf-8-sig")
    write_summary(ladder, args.output_dir)
    print(f"Wrote {out_path}")
    print(f"Wrote {args.output_dir / 'standard_anonymization_ladder_summary.md'}")


if __name__ == "__main__":
    main()
