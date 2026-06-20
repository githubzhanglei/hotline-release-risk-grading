"""Safe synthetic linkage simulation for T-Linkage threat model.

No external identity-bearing data are used. For each pseudonymous person, the
script samples one ticket as a synthetic auxiliary fact record, then joins it
back to the released table using different adversary field capabilities.

Outputs are aggregate only: candidate-set sizes and expected success metrics.
No row-level auxiliary records or candidate lists are exported.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from privacy_utils import monday_week_start, report_date


DEFAULT_INPUT = Path("data_sample/synthetic_hotline_sample.csv")
DEFAULT_OUTPUT_DIR = Path("example_outputs")
RANDOM_STATE = 20260519


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


def make_key(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    cols = [col for col in cols if col in df.columns]
    if not cols:
        return pd.Series(["<GLOBAL>"] * len(df), index=df.index)
    frame = df[cols].fillna("").replace("", "<MISSING>").astype(str)
    key = frame.iloc[:, 0].copy()
    for col in frame.columns[1:]:
        key = key + " || " + frame[col]
    return key


def sample_auxiliary_records(
    df: pd.DataFrame,
    repeated_persons_only: bool = False,
    random_state: int = RANDOM_STATE,
) -> pd.DataFrame:
    base = df[df["person_id"].fillna("").ne("")].copy()
    if repeated_persons_only:
        counts = base["person_id"].value_counts()
        repeated = set(counts[counts >= 2].index)
        base = base[base["person_id"].isin(repeated)].copy()
    base = base.sort_values(["person_id", "ticket_dt", "sample_id"], kind="mergesort")
    # Deterministic pseudo-random sampling per person for reproducibility.
    rng = np.random.default_rng(random_state)
    selected_indices = []
    for _, group in base.groupby("person_id", sort=False):
        selected_indices.append(rng.choice(group.index.to_numpy()))
    return base.loc[selected_indices].copy()


def evaluate_linkage(
    df: pd.DataFrame,
    aux: pd.DataFrame,
    scenario: str,
    cols: list[str],
    scenario_type: str = "exact_auxiliary",
    exclude_aux_ticket: bool = False,
) -> dict[str, object]:
    release = df[df["person_id"].fillna("").ne("")].copy()
    release["_link_key"] = make_key(release, cols)
    aux = aux.copy()
    aux["_link_key"] = make_key(aux, cols)

    if exclude_aux_ticket:
        return evaluate_leave_one_ticket_out(release, aux, scenario, cols, scenario_type)

    group_person_counts = release.groupby("_link_key")["person_id"].nunique()
    group_record_counts = release.groupby("_link_key").size()
    group_top_person = release.groupby("_link_key")["person_id"].agg(lambda s: s.value_counts().idxmax())

    aux["_candidate_persons"] = aux["_link_key"].map(group_person_counts).fillna(0).astype(int)
    aux["_candidate_records"] = aux["_link_key"].map(group_record_counts).fillna(0).astype(int)
    aux["_top_person"] = aux["_link_key"].map(group_top_person).fillna("")

    matched = aux[aux["_candidate_persons"].gt(0)].copy()
    if matched.empty:
        return {
            "scenario": scenario,
            "scenario_type": scenario_type,
            "auxiliary_fields": " + ".join(cols),
            "aux_persons": int(aux["person_id"].nunique()),
            "matched_aux_persons": 0,
            "match_coverage": 0.0,
            "pct_unique_candidate_person": 0.0,
            "pct_candidate_persons_le_5": 0.0,
            "median_candidate_persons": 0.0,
            "mean_candidate_persons": 0.0,
            "map_top_person_success": 0.0,
            "random_within_candidates_success": 0.0,
        }

    return {
        "scenario": scenario,
        "scenario_type": scenario_type,
        "auxiliary_fields": " + ".join(cols),
        "aux_persons": int(aux["person_id"].nunique()),
        "matched_aux_persons": int(len(matched)),
        "match_coverage": float(len(matched) / len(aux)),
        "pct_unique_candidate_person": float(matched["_candidate_persons"].eq(1).mean()),
        "pct_candidate_persons_le_5": float(matched["_candidate_persons"].le(5).mean()),
        "median_candidate_persons": float(matched["_candidate_persons"].median()),
        "mean_candidate_persons": float(matched["_candidate_persons"].mean()),
        "median_candidate_records": float(matched["_candidate_records"].median()),
        "mean_candidate_records": float(matched["_candidate_records"].mean()),
        "map_top_person_success": float(matched["person_id"].eq(matched["_top_person"]).mean()),
        "random_within_candidates_success": float((1.0 / matched["_candidate_persons"].replace(0, np.nan)).mean()),
        "target_still_candidate_coverage": 1.0,
    }


def evaluate_leave_one_ticket_out(
    release: pd.DataFrame,
    aux: pd.DataFrame,
    scenario: str,
    cols: list[str],
    scenario_type: str,
) -> dict[str, object]:
    """Evaluate candidate collapse after removing the auxiliary ticket itself."""

    group_person_counts = release.groupby("_link_key")["person_id"].nunique()
    group_record_counts = release.groupby("_link_key").size()
    pair_counts = release.groupby(["_link_key", "person_id"]).size().rename("pair_count").reset_index()
    pair_counts["top_count"] = pair_counts.groupby("_link_key")["pair_count"].transform("max")
    pair_counts["is_top"] = pair_counts["pair_count"].eq(pair_counts["top_count"])
    top_multiplicity = pair_counts.groupby("_link_key")["is_top"].sum().rename("top_multiplicity")
    second_counts = (
        pair_counts[~pair_counts["is_top"]]
        .groupby("_link_key")["pair_count"]
        .max()
        .rename("second_count")
    )
    pair_counts = pair_counts.join(top_multiplicity, on="_link_key").join(second_counts, on="_link_key")
    pair_counts["second_count"] = pair_counts["second_count"].fillna(0).astype(int)
    pair_counts["max_other_count"] = np.where(
        pair_counts["is_top"] & pair_counts["top_multiplicity"].eq(1),
        pair_counts["second_count"],
        pair_counts["top_count"],
    )

    aux = aux.copy()
    aux["_candidate_persons_before"] = aux["_link_key"].map(group_person_counts).fillna(0).astype(int)
    aux["_candidate_records_before"] = aux["_link_key"].map(group_record_counts).fillna(0).astype(int)

    pair_lookup = pair_counts.set_index(["_link_key", "person_id"])
    keys = pd.MultiIndex.from_frame(aux[["_link_key", "person_id"]])
    aux["_target_records_before"] = pair_lookup["pair_count"].reindex(keys).fillna(0).to_numpy(dtype=int)
    aux["_max_other_count"] = pair_lookup["max_other_count"].reindex(keys).fillna(0).to_numpy(dtype=int)

    aux["_target_records_after"] = (aux["_target_records_before"] - 1).clip(lower=0)
    aux["_candidate_records"] = (aux["_candidate_records_before"] - 1).clip(lower=0)
    aux["_candidate_persons"] = aux["_candidate_persons_before"] - aux["_target_records_after"].eq(0).astype(int)
    aux["_candidate_persons"] = aux["_candidate_persons"].clip(lower=0)
    aux["_target_still_candidate"] = aux["_target_records_after"].gt(0)
    # Modal success is an optimistic MAP proxy under ties after the seed row is removed.
    aux["_modal_target_success"] = aux["_target_still_candidate"] & (
        aux["_target_records_after"] >= aux["_max_other_count"]
    )

    matched = aux[aux["_candidate_persons"].gt(0)].copy()
    if matched.empty:
        return {
            "scenario": scenario,
            "scenario_type": scenario_type,
            "auxiliary_fields": " + ".join(cols),
            "aux_persons": int(aux["person_id"].nunique()),
            "matched_aux_persons": 0,
            "match_coverage": 0.0,
            "target_still_candidate_coverage": 0.0,
            "pct_unique_candidate_person": 0.0,
            "pct_candidate_persons_le_5": 0.0,
            "median_candidate_persons": 0.0,
            "mean_candidate_persons": 0.0,
            "median_candidate_records": 0.0,
            "mean_candidate_records": 0.0,
            "map_top_person_success": 0.0,
            "random_within_candidates_success": 0.0,
        }

    random_success = np.where(
        matched["_target_still_candidate"],
        1.0 / matched["_candidate_persons"].replace(0, np.nan),
        0.0,
    )
    return {
        "scenario": scenario,
        "scenario_type": scenario_type,
        "auxiliary_fields": " + ".join(cols),
        "aux_persons": int(aux["person_id"].nunique()),
        "matched_aux_persons": int(len(matched)),
        "match_coverage": float(len(matched) / len(aux)),
        "target_still_candidate_coverage": float(matched["_target_still_candidate"].mean()),
        "pct_unique_candidate_person": float(matched["_candidate_persons"].eq(1).mean()),
        "pct_candidate_persons_le_5": float(matched["_candidate_persons"].le(5).mean()),
        "median_candidate_persons": float(matched["_candidate_persons"].median()),
        "mean_candidate_persons": float(matched["_candidate_persons"].mean()),
        "median_candidate_records": float(matched["_candidate_records"].median()),
        "mean_candidate_records": float(matched["_candidate_records"].mean()),
        "map_top_person_success": float(matched["_modal_target_success"].mean()),
        "random_within_candidates_success": float(np.nanmean(random_success)),
    }


def run_simulation(df: pd.DataFrame, random_state: int = RANDOM_STATE) -> pd.DataFrame:
    aux = sample_auxiliary_records(df, random_state=random_state)
    aux_repeated = sample_auxiliary_records(df, repeated_persons_only=True, random_state=random_state)
    scenarios = [
        ("street_topic_no_week", ["区县地址", "街道地址", "mapped_l2_name"], "exact_auxiliary"),
        ("street_week_l1", ["区县地址", "街道地址", "week_start", "mapped_l1_name"], "exact_auxiliary"),
        ("street_week_l2", ["区县地址", "街道地址", "week_start", "mapped_l2_name"], "exact_auxiliary"),
        ("street_week_l2_process", ["区县地址", "街道地址", "week_start", "mapped_l2_name", "问题是否解决"], "exact_auxiliary"),
        ("street_week_l2_place_type", ["区县地址", "街道地址", "week_start", "mapped_l2_name", "text_place_type"], "exact_auxiliary"),
        ("street_week_l2_subject_type", ["区县地址", "街道地址", "week_start", "mapped_l2_name", "text_subject_type"], "exact_auxiliary"),
        ("street_week_l2_text_place_id", ["区县地址", "街道地址", "week_start", "mapped_l2_name", "text_place_id"], "exact_auxiliary"),
        ("street_week_l2_address_id", ["区县地址", "街道地址", "week_start", "mapped_l2_name", "address_id"], "exact_auxiliary"),
        (
            "street_week_l2_relation_keys",
            ["区县地址", "街道地址", "week_start", "mapped_l2_name", "address_id", "text_place_id"],
            "exact_auxiliary",
        ),
        ("degraded_no_week_text_place_id", ["区县地址", "街道地址", "mapped_l2_name", "text_place_id"], "degraded_auxiliary"),
        ("degraded_month_text_place_id", ["区县地址", "街道地址", "month_start", "mapped_l2_name", "text_place_id"], "degraded_auxiliary"),
        ("degraded_l1_week_text_place_id", ["区县地址", "街道地址", "week_start", "mapped_l1_name", "text_place_id"], "degraded_auxiliary"),
        ("degraded_no_week_address_id", ["区县地址", "街道地址", "mapped_l2_name", "address_id"], "degraded_auxiliary"),
        ("degraded_month_address_id", ["区县地址", "街道地址", "month_start", "mapped_l2_name", "address_id"], "degraded_auxiliary"),
        (
            "degraded_month_relation_keys",
            ["区县地址", "街道地址", "month_start", "mapped_l2_name", "address_id", "text_place_id"],
            "degraded_auxiliary",
        ),
    ]
    rows = []
    for scenario, cols, scenario_type in scenarios:
        rows.append(
            evaluate_linkage(
                df,
                aux,
                scenario,
                cols,
                f"{scenario_type}__same_row_included",
                exclude_aux_ticket=False,
            )
        )
        rows.append(
            evaluate_linkage(
                df,
                aux,
                scenario,
                cols,
                f"{scenario_type}__leave_one_ticket_out_all",
                exclude_aux_ticket=True,
            )
        )
        rows.append(
            evaluate_linkage(
                df,
                aux_repeated,
                scenario,
                cols,
                f"{scenario_type}__leave_one_ticket_out_repeated",
                exclude_aux_ticket=True,
            )
        )
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
        values = [str(row[col]).replace("\n", " ") for col in cols]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_summary(results: pd.DataFrame, output_dir: Path) -> None:
    display = results.copy()
    for col in [
        "match_coverage",
        "target_still_candidate_coverage",
        "pct_unique_candidate_person",
        "pct_candidate_persons_le_5",
        "map_top_person_success",
        "random_within_candidates_success",
    ]:
        display[col] = (display[col].astype(float) * 100).round(2)
    for col in ["median_candidate_persons", "mean_candidate_persons", "median_candidate_records", "mean_candidate_records"]:
        if col in display.columns:
            display[col] = display[col].astype(float).round(2)

    key_cols = [
        "scenario",
        "scenario_type",
        "matched_aux_persons",
        "match_coverage",
        "target_still_candidate_coverage",
        "pct_unique_candidate_person",
        "pct_candidate_persons_le_5",
        "median_candidate_persons",
        "mean_candidate_persons",
        "map_top_person_success",
        "random_within_candidates_success",
    ]
    lines = [
        "# Safe Synthetic T-Linkage Simulation",
        "",
        f"Date: {report_date()}",
        "",
        "No external identity-bearing data are used. Each auxiliary row is a synthetic known-fact record sampled from one pseudonymous person's ticket history.",
        "The result quantifies joinability and candidate-set collapse, not real-world legal identity recovery.",
        "",
        "## Results",
        "",
        to_markdown_table(display[key_cols]),
        "",
        "## Interpretation Boundary",
        "",
        "- This is a controlled joinability proxy for T-Linkage.",
        "- Degraded auxiliary scenarios remove week precision or lower topic precision so the result is not only an exact same-row upper bound.",
        "- Leave-one-ticket-out scenarios remove the synthetic auxiliary ticket from the release table before joining.",
        "- It should not be described as an attack on real citizens.",
        "- Strong results under `address_id` and `text_place_id` mean those fields create small candidate sets when an adversary has matching facts.",
    ]
    (output_dir / "synthetic_linkage_simulation_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--random-state", type=int, default=RANDOM_STATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.input)
    df = normalize_columns(df)
    results = run_simulation(df, random_state=args.random_state)
    out_path = args.output_dir / "synthetic_linkage_simulation.csv"
    results.to_csv(out_path, index=False, encoding="utf-8-sig")
    write_summary(results, args.output_dir)
    print(f"Wrote {out_path}")
    print(f"Wrote {args.output_dir / 'synthetic_linkage_simulation_summary.md'}")


if __name__ == "__main__":
    main()
