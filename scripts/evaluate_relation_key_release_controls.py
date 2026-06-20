"""Evaluate release controls for stable relation keys.

The goal is to turn the risk audit into publishable release guidance:
what happens if address/place relation keys are suppressed by empirical
person-diversity thresholds or generalized to coarser types?

All outputs are aggregate metrics. No raw text, raw identifiers, or row-level
candidate sets are exported.
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
BASE_QID = ["区县地址", "街道地址", "week_start", "mapped_l2_name"]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ticket_dt"] = pd.to_datetime(out["ticket_date"], errors="coerce")
    out["week_start"] = monday_week_start(out["ticket_dt"])
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


def binary_entropy_bits(p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return float(-(p * math.log2(p) + (1 - p) * math.log2(1 - p)))


def fano_error_lower_bound_bits(mutual_info_bits: float, num_classes: int) -> float:
    if num_classes <= 1:
        return 0.0
    return max(0.0, 1.0 - ((mutual_info_bits + 1.0) / math.log2(num_classes)))


def make_key(df: pd.DataFrame, cols: list[str]) -> pd.Series:
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
        "scenario": label,
        "qid_columns": " + ".join(cols),
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
        "fano_error_lb_uniform": fano_error_lower_bound_bits(mi_bits, num_persons),
    }


def suppress_by_person_diversity(df: pd.DataFrame, col: str, threshold: int, out_col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series(["<MISSING>"] * len(df), index=df.index)
    nonempty = df[col].fillna("").astype(str).str.strip()
    person_diversity = df[nonempty.ne("")].groupby(col)["person_id"].nunique()
    safe_values = set(person_diversity[person_diversity >= threshold].index.astype(str))
    return nonempty.map(lambda value: value if value in safe_values else f"<SUPPRESSED_{out_col}>")


def retained_stats(df: pd.DataFrame, original_col: str, controlled_col: str) -> dict[str, object]:
    if original_col not in df.columns or controlled_col not in df.columns:
        return {
            f"{controlled_col}_retained_record_pct": 0.0,
            f"{controlled_col}_retained_distinct_pct": 0.0,
        }
    original = df[original_col].fillna("").astype(str).str.strip()
    controlled = df[controlled_col].fillna("").astype(str).str.strip()
    nonempty = original.ne("")
    retained = nonempty & ~controlled.str.startswith("<SUPPRESSED")
    distinct_original = set(original[nonempty])
    distinct_retained = set(controlled[retained])
    return {
        f"{controlled_col}_retained_record_pct": float(retained.mean()),
        f"{controlled_col}_retained_distinct_pct": float(len(distinct_retained) / len(distinct_original))
        if distinct_original
        else 0.0,
    }


def add_delta(row: dict[str, object], baseline: dict[str, object]) -> dict[str, object]:
    row = dict(row)
    row["delta_k1_vs_topic_only_pp"] = (float(row["pct_records_k1"]) - float(baseline["pct_records_k1"])) * 100.0
    row["delta_map_vs_topic_only_pp"] = (
        float(row["map_reid_accuracy"]) - float(baseline["map_reid_accuracy"])
    ) * 100.0
    row["delta_i_bits_vs_topic_only"] = float(row["i_struct_empirical_bits"]) - float(
        baseline["i_struct_empirical_bits"]
    )
    return row


def build_release_control_sweep(df: pd.DataFrame, thresholds: list[int]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    baseline = evaluate_qid_combo(df, "topic_only", BASE_QID)
    rows.append(
        {
            **baseline,
            "control_type": "baseline",
            "threshold_persons": 0,
            "release_guidance": "minimum structural release baseline",
        }
    )

    raw_scenarios = [
        ("raw_text_place_id", BASE_QID + ["text_place_id"], "raw relation key; unsafe"),
        ("raw_address_id", BASE_QID + ["address_id"], "raw stable address key; unsafe"),
        ("raw_relation_keys", BASE_QID + ["address_id", "text_place_id"], "raw combined relation keys; unsafe"),
        ("text_place_type_only", BASE_QID + ["text_place_type"], "generalize text place key to type"),
        ("text_subject_type_only", BASE_QID + ["text_subject_type"], "generalize text subject key to type"),
        (
            "place_subject_types_only",
            BASE_QID + ["text_place_type", "text_subject_type"],
            "generalize text relation keys to coarse types",
        ),
        (
            "presence_flags_only",
            BASE_QID + ["has_address_id", "has_text_place_id", "has_text_subject_id"],
            "release only whether a relation key exists",
        ),
    ]
    for label, cols, guidance in raw_scenarios:
        row = evaluate_qid_combo(df, label, cols)
        row.update({"control_type": "raw_or_generalized", "threshold_persons": 0, "release_guidance": guidance})
        rows.append(add_delta(row, baseline))

    for threshold in thresholds:
        controlled = df.copy()
        controlled[f"address_id_k{threshold}"] = suppress_by_person_diversity(
            controlled, "address_id", threshold, f"address_id_k{threshold}"
        )
        controlled[f"text_place_id_k{threshold}"] = suppress_by_person_diversity(
            controlled, "text_place_id", threshold, f"text_place_id_k{threshold}"
        )
        controlled[f"text_subject_id_k{threshold}"] = suppress_by_person_diversity(
            controlled, "text_subject_id", threshold, f"text_subject_id_k{threshold}"
        )

        scenarios = [
            (
                f"address_id_k{threshold}",
                BASE_QID + [f"address_id_k{threshold}"],
                "threshold-suppress address keys below person-diversity k",
                ["address_id"],
            ),
            (
                f"text_place_id_k{threshold}",
                BASE_QID + [f"text_place_id_k{threshold}"],
                "threshold-suppress text place keys below person-diversity k",
                ["text_place_id"],
            ),
            (
                f"text_subject_id_k{threshold}",
                BASE_QID + [f"text_subject_id_k{threshold}"],
                "threshold-suppress text subject keys below person-diversity k",
                ["text_subject_id"],
            ),
            (
                f"relation_keys_k{threshold}",
                BASE_QID + [f"address_id_k{threshold}", f"text_place_id_k{threshold}"],
                "threshold-suppress both address and text-place keys below person-diversity k",
                ["address_id", "text_place_id"],
            ),
        ]
        for label, cols, guidance, originals in scenarios:
            row = evaluate_qid_combo(controlled, label, cols)
            row.update(
                {
                    "control_type": "threshold_suppression",
                    "threshold_persons": threshold,
                    "release_guidance": guidance,
                }
            )
            for original in originals:
                controlled_col = f"{original}_k{threshold}"
                row.update(retained_stats(controlled, original, controlled_col))
            rows.append(add_delta(row, baseline))

    out = pd.DataFrame(rows)
    for col in [
        "delta_k1_vs_topic_only_pp",
        "delta_map_vs_topic_only_pp",
        "delta_i_bits_vs_topic_only",
    ]:
        if col not in out.columns:
            out[col] = 0.0
    return out


def to_markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in df.iterrows():
        values = [str(row[col]).replace("\n", " ") for col in cols]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_summary(results: pd.DataFrame, output_dir: Path) -> None:
    path = output_dir / "relation_key_release_control_summary.md"
    display = results.copy()
    pct_cols = [
        "pct_records_k1",
        "pct_records_k_le_5",
        "map_reid_accuracy",
    ]
    for col in pct_cols:
        display[col] = (display[col].astype(float) * 100).round(2)
    for col in [
        "i_struct_empirical_bits",
        "effective_person_candidates",
        "delta_i_bits_vs_topic_only",
        "delta_k1_vs_topic_only_pp",
        "delta_map_vs_topic_only_pp",
    ]:
        display[col] = display[col].astype(float).round(3)

    key_cols = [
        "scenario",
        "control_type",
        "threshold_persons",
        "pct_records_k1",
        "pct_records_k_le_5",
        "map_reid_accuracy",
        "i_struct_empirical_bits",
        "effective_person_candidates",
        "delta_k1_vs_topic_only_pp",
        "delta_map_vs_topic_only_pp",
        "release_guidance",
    ]

    selected = display[
        display["scenario"].isin(
            [
                "topic_only",
                "raw_text_place_id",
                "raw_address_id",
                "raw_relation_keys",
                "text_place_type_only",
                "presence_flags_only",
                "relation_keys_k2",
                "relation_keys_k5",
                "relation_keys_k10",
                "relation_keys_k20",
                "relation_keys_k50",
            ]
        )
    ][key_cols]

    best_safe = display[
        (display["control_type"].eq("threshold_suppression"))
        & (display["scenario"].str.startswith("relation_keys_k"))
    ].sort_values(["map_reid_accuracy", "pct_records_k1"]).head(1)

    lines = [
        "# Relation-key Release Control Sweep",
        "",
        f"Date: {report_date()}",
        "",
        "Privacy unit: pseudonymous `person_id`.",
        "Controls suppress relation-key values whose empirical person-diversity is below a threshold.",
        "",
        "## Selected Results",
        "",
        to_markdown_table(selected),
        "",
        "## Current Best Suppression Row",
        "",
        to_markdown_table(best_safe[key_cols]) if not best_safe.empty else "_No threshold rows._",
        "",
        "## Interpretation Boundary",
        "",
        "- Suppression thresholds are empirical controls for this snapshot, not formal privacy guarantees.",
        "- Generalizing relation keys to coarse types is safer than releasing raw stable keys, but it does not replace DP for public aggregate release.",
        "- A publishable defense section should combine key suppression/generalization with bounded-contribution DP for released statistics.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--thresholds", type=int, nargs="*", default=[2, 5, 10, 20, 50])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.input)
    df = normalize_columns(df)
    results = build_release_control_sweep(df, thresholds=args.thresholds)
    out_path = args.output_dir / "relation_key_release_control_sweep.csv"
    results.to_csv(out_path, index=False, encoding="utf-8-sig")
    write_summary(results, args.output_dir)
    print(f"Wrote {out_path}")
    print(f"Wrote {args.output_dir / 'relation_key_release_control_summary.md'}")


if __name__ == "__main__":
    main()
