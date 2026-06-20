"""Analyze re-identification risk in the de-identified hotline snapshot.

The script writes aggregate-only privacy audit artifacts. It does not export raw
ticket text, raw identifiers, or row-level candidate sets.
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import entropy as scipy_entropy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC

from privacy_utils import monday_week_start


DEFAULT_INPUT = Path("data_sample/synthetic_hotline_sample.csv")
DEFAULT_OUTPUT_DIR = Path("example_outputs")


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


def fano_mi_lower_bound_bits(error_rate: float, num_classes: int) -> float:
    if num_classes <= 1:
        return 0.0
    upper_conditional = binary_entropy_bits(error_rate) + error_rate * math.log2(num_classes - 1)
    return max(0.0, math.log2(num_classes) - upper_conditional)


def fano_error_lower_bound_bits(mutual_info_bits: float, num_classes: int) -> float:
    if num_classes <= 1:
        return 0.0
    return max(0.0, 1.0 - ((mutual_info_bits + 1.0) / math.log2(num_classes)))


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ticket_dt"] = pd.to_datetime(out["ticket_date"], errors="coerce")
    out["week_start"] = monday_week_start(out["ticket_dt"])

    def bin_count(value: object) -> str:
        try:
            count = int(float(value))
        except (TypeError, ValueError):
            return "missing"
        if count <= 1:
            return "1"
        if count <= 3:
            return "2-3"
        if count <= 9:
            return "4-9"
        return "10+"

    out["person_recurrence_bin"] = out.get("person_total_complaints", pd.Series(index=out.index, dtype=str)).map(
        bin_count
    )
    out["address_recurrence_bin"] = out.get("address_total_complaints", pd.Series(index=out.index, dtype=str)).map(
        bin_count
    )

    for col in out.columns:
        if out[col].dtype == object:
            out[col] = out[col].fillna("").astype(str).str.strip()
    return out


def existing_columns(cols: list[str], df: pd.DataFrame) -> list[str]:
    return [col for col in cols if col in df.columns]


def make_key(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    if not cols:
        return pd.Series(["<GLOBAL>"] * len(df), index=df.index)
    return df[cols].fillna("").replace("", "<MISSING>").astype(str).agg(" || ".join, axis=1)


def evaluate_qid_combo(df: pd.DataFrame, label: str, cols: list[str]) -> dict[str, object]:
    person_df = df[df["person_id"].fillna("").ne("")].copy()
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
    random_expected_accuracy = float((1.0 / record_person_l.replace(0, np.nan)).mean())

    return {
        "qid_label": label,
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
        "i_struct_normalized": float(mi_bits / h_person) if h_person > 0 else 0.0,
        "effective_person_candidates": float(2**h_person_given_q),
        "map_reid_accuracy": map_accuracy,
        "random_within_qid_accuracy": random_expected_accuracy,
        "fano_error_lb_uniform": fano_error_lower_bound_bits(mi_bits, num_persons),
    }


def qid_sweep(df: pd.DataFrame) -> pd.DataFrame:
    combos = [
        ("T0_global", []),
        ("T1_district_street_week", ["区县地址", "街道地址", "week_start"]),
        ("T2_plus_l1", ["区县地址", "街道地址", "week_start", "mapped_l1_name"]),
        ("T2_plus_l2", ["区县地址", "街道地址", "week_start", "mapped_l2_name"]),
        ("T3_plus_callback", ["区县地址", "街道地址", "week_start", "mapped_l2_name", "是否回访"]),
        ("T3_plus_solved", ["区县地址", "街道地址", "week_start", "mapped_l2_name", "问题是否解决"]),
        ("T3_plus_hotspot", ["区县地址", "街道地址", "week_start", "mapped_l2_name", "是否热点"]),
        ("T3_plus_person_recur_bin", ["区县地址", "街道地址", "week_start", "mapped_l2_name", "person_recurrence_bin"]),
        ("T3_plus_address_recur_bin", ["区县地址", "街道地址", "week_start", "mapped_l2_name", "address_recurrence_bin"]),
        ("T3_plus_undertaking_unit", ["区县地址", "街道地址", "week_start", "mapped_l2_name", "承办单位"]),
        ("T4_plus_text_subject", ["区县地址", "街道地址", "week_start", "mapped_l2_name", "text_subject_id"]),
        ("T4_plus_text_place", ["区县地址", "街道地址", "week_start", "mapped_l2_name", "text_place_id"]),
        ("T4_plus_address_id", ["区县地址", "街道地址", "week_start", "mapped_l2_name", "address_id"]),
        ("T4_plus_relation_keys", ["区县地址", "街道地址", "week_start", "mapped_l2_name", "address_id", "text_place_id"]),
    ]
    rows = []
    for label, cols in combos:
        cols = existing_columns(cols, df)
        rows.append(evaluate_qid_combo(df, label, cols))
    return pd.DataFrame(rows)


def recurrence_distribution(df: pd.DataFrame) -> pd.DataFrame:
    person_counts = df.loc[df["person_id"].ne(""), "person_id"].value_counts()
    bins = [
        ("1", person_counts.eq(1)),
        ("2", person_counts.eq(2)),
        ("3", person_counts.eq(3)),
        ("4-5", person_counts.between(4, 5)),
        ("6-9", person_counts.between(6, 9)),
        ("10+", person_counts.ge(10)),
    ]
    rows = []
    for label, mask in bins:
        counts = person_counts[mask]
        rows.append(
            {
                "ticket_count_bin": label,
                "num_persons": int(len(counts)),
                "num_tickets": int(counts.sum()),
                "pct_persons": float(len(counts) / len(person_counts)) if len(person_counts) else 0.0,
                "pct_tickets": float(counts.sum() / person_counts.sum()) if person_counts.sum() else 0.0,
            }
        )
    return pd.DataFrame(rows)


def nstar_sensitivity(qid_results: pd.DataFrame) -> pd.DataFrame:
    rows = []
    base_rows = qid_results[qid_results["qid_label"].isin(["T2_plus_l2", "T3_plus_person_recur_bin", "T4_plus_text_place"])]
    for _, row in base_rows.iterrows():
        h_identity = float(row["h_person_bits"])
        for i_style in [0.01, 0.05, 0.10, 0.25, 0.50, 1.00]:
            # Fano-style certificate horizon: above this point the lower bound
            # can become vacuous; this is not an attack-success threshold.
            remaining = max(0.0, h_identity - float(row["i_struct_empirical_bits"]) - 1.0)
            rows.append(
                {
                    "qid_label": row["qid_label"],
                    "h_person_bits": h_identity,
                    "i_struct_empirical_bits": float(row["i_struct_empirical_bits"]),
                    "assumed_i_style_bits_per_ticket": i_style,
                    "n_certificate_horizon": int(math.ceil(remaining / i_style)) if i_style > 0 else None,
                    "interpretation": "Fano lower-bound horizon; not a successful re-identification threshold.",
                }
            )
    return pd.DataFrame(rows)


ID_TOKEN_RE = re.compile(r"\[(?:地址ID|主体ID|地点ID|电话|姓名|身份证号?|车牌号?|编号)[^\]]*\]")
HASH_TOKEN_RE = re.compile(r"\b(?:A|P|TP|TS|C)_[0-9a-f]{8,}\b", flags=re.IGNORECASE)
DIGIT_RE = re.compile(r"[0-9０-９]+")


def clean_text_variant(text: str, variant: str) -> str:
    text = "" if pd.isna(text) else str(text)
    if variant == "full_sanitized":
        return text
    text = ID_TOKEN_RE.sub(" [占位符] ", text)
    text = HASH_TOKEN_RE.sub(" [哈希ID] ", text)
    if variant == "remove_stable_ids":
        return text
    text = DIGIT_RE.sub("0", text)
    text = re.sub(r"[A-Za-z_]+", " ", text)
    return text


def stylometric_prelim(df: pd.DataFrame, output_dir: Path, max_persons: int = 300) -> pd.DataFrame:
    text_col = "sanitized_text"
    base = df[(df["person_id"].ne("")) & (df[text_col].fillna("").str.len() >= 25)].copy()
    counts = base["person_id"].value_counts()
    eligible = counts[counts >= 3].head(max_persons).index
    base = base[base["person_id"].isin(eligible)].copy()
    if base["person_id"].nunique() < 10:
        return pd.DataFrame()

    rows = []
    for variant in ["full_sanitized", "remove_stable_ids", "remove_ids_digits_ascii"]:
        texts = base[text_col].map(lambda x: clean_text_variant(x, variant))
        y = base["person_id"].to_numpy()
        x_train, x_test, y_train, y_test = train_test_split(
            texts.to_numpy(),
            y,
            test_size=0.34,
            random_state=20260517,
            stratify=y,
        )
        vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 4), min_df=2, max_features=60000)
        x_train_vec = vectorizer.fit_transform(x_train)
        x_test_vec = vectorizer.transform(x_test)
        clf = LinearSVC(C=1.0, random_state=20260517, dual="auto")
        clf.fit(x_train_vec, y_train)
        pred = clf.predict(x_test_vec)
        top1 = float(accuracy_score(y_test, pred))
        scores = clf.decision_function(x_test_vec)
        classes = clf.classes_
        top5 = 0.0
        if scores.ndim == 1:
            top5 = top1
        else:
            top_idx = np.argpartition(scores, -min(5, scores.shape[1]), axis=1)[:, -min(5, scores.shape[1]) :]
            top5 = float(np.mean([y_test[i] in classes[top_idx[i]] for i in range(len(y_test))]))
        num_classes = int(base["person_id"].nunique())
        error = 1.0 - top1
        rows.append(
            {
                "variant": variant,
                "num_persons": num_classes,
                "num_records": int(len(base)),
                "train_records": int(len(x_train)),
                "test_records": int(len(x_test)),
                "top1_accuracy": top1,
                "top5_accuracy": top5,
                "random_top1": 1.0 / num_classes,
                "fano_mi_lower_bound_bits": fano_mi_lower_bound_bits(error, num_classes),
                "notes": "Person-attribution proxy; captures residual content/topic/place signals, not pure writing style.",
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(output_dir / "stylometric_attribution_prelim.csv", index=False, encoding="utf-8-sig")
    return out


def write_summary(
    output_dir: Path,
    qid: pd.DataFrame,
    recurrence: pd.DataFrame,
    nstar: pd.DataFrame,
    stylometry: pd.DataFrame,
) -> None:
    lines = [
        "# Privacy Re-identification Risk Audit",
        "",
        "Generated by `scripts/analyze_privacy_reidentification_risk.py`.",
        "",
        "## Key Findings",
        "",
    ]

    selected = qid[qid["qid_label"].isin(["T1_district_street_week", "T2_plus_l2", "T3_plus_person_recur_bin", "T4_plus_text_place", "T4_plus_address_id"])]
    for _, row in selected.iterrows():
        lines.append(
            f"- `{row['qid_label']}`: k=1 {row['pct_records_k1']:.1%}, "
            f"k<=5 {row['pct_records_k_le_5']:.1%}, "
            f"MAP re-id {row['map_reid_accuracy']:.1%}, "
            f"I_struct {row['i_struct_empirical_bits']:.2f} bits."
        )

    repeated = recurrence[recurrence["ticket_count_bin"].ne("1")]
    lines.extend(
        [
            "",
            "## Person Recurrence",
            "",
            f"- Repeated callers/person IDs: {int(repeated['num_persons'].sum())}.",
            f"- Tickets from repeated callers/person IDs: {int(repeated['num_tickets'].sum())}.",
            "",
            "## Caveats",
            "",
            "- `subject_id` is structurally unavailable in the raw export; use `text_subject_id` only as a noisy text-derived proxy.",
            "- The mutual-information values are empirical plug-in estimates over pseudonymous `person_id`; they are suitable for internal audit and theorem calibration, not population-level guarantees without bias analysis.",
            "- The stylometric experiment is a residual-text attribution proxy. It can include topic, address residue, and repeated complaint content; do not claim pure authorship style without stronger controls.",
            "- Fano lower bounds are reported as converse diagnostics. The `n_certificate_horizon` sensitivity table marks where the lower bound can become vacuous; it does not prove that people above that horizon are identifiable.",
        ]
    )
    if not stylometry.empty:
        lines.extend(["", "## Preliminary Residual-text Attribution", ""])
        for _, row in stylometry.iterrows():
            lines.append(
                f"- `{row['variant']}`: top-1 {row['top1_accuracy']:.1%}, "
                f"top-5 {row['top5_accuracy']:.1%}, random top-1 {row['random_top1']:.2%}, "
                f"Fano MI lower bound {row['fano_mi_lower_bound_bits']:.2f} bits."
            )

    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- `k_anonymity_full_sweep.csv`",
            "- `person_recurrence_distribution.csv`",
            "- `nstar_sensitivity.csv`",
            "- `stylometric_attribution_prelim.csv`",
        ]
    )
    (output_dir / "privacy_risk_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--skip-stylometry", action="store_true")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.input, dtype=str)
    df = normalize_columns(df)

    qid = qid_sweep(df)
    qid.to_csv(args.output_dir / "k_anonymity_full_sweep.csv", index=False, encoding="utf-8-sig")

    recurrence = recurrence_distribution(df)
    recurrence.to_csv(args.output_dir / "person_recurrence_distribution.csv", index=False, encoding="utf-8-sig")

    nstar = nstar_sensitivity(qid)
    nstar.to_csv(args.output_dir / "nstar_sensitivity.csv", index=False, encoding="utf-8-sig")

    stylometry = pd.DataFrame()
    if not args.skip_stylometry:
        stylometry = stylometric_prelim(df, args.output_dir)

    write_summary(args.output_dir, qid, recurrence, nstar, stylometry)
    print(f"Wrote privacy risk audit artifacts to {args.output_dir}")


if __name__ == "__main__":
    main()
