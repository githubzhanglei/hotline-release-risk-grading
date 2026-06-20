"""Seed sensitivity for the synthetic T-Linkage experiment.

The main synthetic linkage script samples one auxiliary ticket per pseudonymous
person. This script reruns the paper-critical repeated-person scenarios over
multiple deterministic seeds so the manuscript can report sampling stability.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from privacy_utils import report_date
from simulate_synthetic_linkage_attack import (
    evaluate_linkage,
    normalize_columns,
    sample_auxiliary_records,
)


DEFAULT_INPUT = Path("data_sample/synthetic_hotline_sample.csv")
DEFAULT_OUTPUT_DIR = Path("example_outputs")
DEFAULT_SEED_START = 20260500
DEFAULT_TRIALS = 30

SCENARIOS = [
    (
        "street_week_l2_relation_keys",
        ["区县地址", "街道地址", "week_start", "mapped_l2_name", "address_id", "text_place_id"],
        "exact_auxiliary__leave_one_ticket_out_repeated",
    ),
    (
        "degraded_month_relation_keys",
        ["区县地址", "街道地址", "month_start", "mapped_l2_name", "address_id", "text_place_id"],
        "degraded_auxiliary__leave_one_ticket_out_repeated",
    ),
]

SUMMARY_METRICS = [
    "match_coverage",
    "target_still_candidate_coverage",
    "pct_unique_candidate_person",
    "pct_candidate_persons_le_5",
    "map_top_person_success",
    "random_within_candidates_success",
    "median_candidate_persons",
]


def run_trials(df: pd.DataFrame, seed_start: int, trials: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for offset in range(trials):
        seed = seed_start + offset
        aux_repeated = sample_auxiliary_records(df, repeated_persons_only=True, random_state=seed)
        for scenario, cols, scenario_type in SCENARIOS:
            row = evaluate_linkage(
                df,
                aux_repeated,
                scenario,
                cols,
                scenario_type,
                exclude_aux_ticket=True,
            )
            row["seed"] = seed
            rows.append(row)
    return pd.DataFrame(rows)


def summarize(trials: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for scenario, group in trials.groupby("scenario", sort=False):
        out: dict[str, object] = {
            "scenario": scenario,
            "scenario_type": group["scenario_type"].iloc[0],
            "trials": int(group["seed"].nunique()),
            "aux_persons": int(group["aux_persons"].median()),
        }
        for metric in SUMMARY_METRICS:
            values = pd.to_numeric(group[metric], errors="coerce")
            out[f"{metric}_mean"] = float(values.mean())
            out[f"{metric}_p10"] = float(values.quantile(0.10))
            out[f"{metric}_p90"] = float(values.quantile(0.90))
            out[f"{metric}_min"] = float(values.min())
            out[f"{metric}_max"] = float(values.max())
        rows.append(out)
    return pd.DataFrame(rows)


def pct(value: object) -> str:
    return f"{float(value) * 100:.2f}%"


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


def write_summary(summary: pd.DataFrame, output_dir: Path) -> None:
    display_rows: list[dict[str, object]] = []
    for _, row in summary.iterrows():
        display_rows.append(
            {
                "scenario": row["scenario"],
                "trials": int(row["trials"]),
                "match coverage mean": pct(row["match_coverage_mean"]),
                "match coverage p10-p90": f"{pct(row['match_coverage_p10'])} - {pct(row['match_coverage_p90'])}",
                "unique among matched mean": pct(row["pct_unique_candidate_person_mean"]),
                "unique among matched p10-p90": f"{pct(row['pct_unique_candidate_person_p10'])} - {pct(row['pct_unique_candidate_person_p90'])}",
                "MAP top-person mean": pct(row["map_top_person_success_mean"]),
                "MAP top-person p10-p90": f"{pct(row['map_top_person_success_p10'])} - {pct(row['map_top_person_success_p90'])}",
                "median candidates mean": f"{float(row['median_candidate_persons_mean']):.2f}",
            }
        )

    lines = [
        "# Synthetic T-Linkage Seed Sensitivity",
        "",
        f"Date: {report_date()}",
        "",
        "Purpose: test whether the leave-one-ticket-out repeated-person linkage results depend on a single auxiliary-ticket sampling seed.",
        "",
        "## Summary",
        "",
        to_markdown_table(pd.DataFrame(display_rows)),
        "",
        "## Interpretation",
        "",
        "- Exact week + both relation keys remains a narrow-coverage but high-collapse repeated-profile linkage setting.",
        "- Degraded month + both relation keys has higher match coverage because the auxiliary fact is less restrictive, while still producing mostly one-person candidate sets among matched traces.",
        "- These are pseudonym-linkage stability checks, not real-world identity recovery attacks.",
    ]
    (output_dir / "synthetic_linkage_seed_sensitivity_summary.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed-start", type=int, default=DEFAULT_SEED_START)
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    df = normalize_columns(pd.read_csv(args.input))
    trial_rows = run_trials(df, seed_start=args.seed_start, trials=args.trials)
    summary = summarize(trial_rows)

    trial_path = args.output_dir / "synthetic_linkage_seed_sensitivity_trials.csv"
    summary_path = args.output_dir / "synthetic_linkage_seed_sensitivity.csv"
    trial_rows.to_csv(trial_path, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    write_summary(summary, args.output_dir)
    print(f"Wrote {trial_path}")
    print(f"Wrote {summary_path}")
    print(f"Wrote {args.output_dir / 'synthetic_linkage_seed_sensitivity_summary.md'}")


if __name__ == "__main__":
    main()
