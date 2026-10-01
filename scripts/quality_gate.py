"""Independently check an actual structured candidate CSV before release review.

The check is a record-group screen, not a legal anonymization certification.
Only aggregate audit information is written; human authorization stays blank.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

import pandas as pd


def column_hash(columns: list[str]) -> str:
    """Bind review to the entire delivered column list, including its order."""
    payload = json.dumps(columns, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def check_candidate(
    candidate: Path,
    *,
    qid_sets: list[list[str]],
    n_in: int,
    snapshot_id: str,
    k: int,
    minimum_retention: float = 0.0,
    expected_column_hash: str | None = None,
) -> dict:
    """Read the delivered bytes and check the union of all declared QIDs."""
    if k < 2 or n_in < 0 or not 0 <= minimum_retention <= 1:
        raise ValueError("Invalid k, input count, or retention parameter.")
    payload = candidate.read_bytes()
    text = payload.decode("utf-8-sig")
    columns = next(csv.reader(io.StringIO(text)), [])
    if not columns or len(set(columns)) != len(columns):
        raise ValueError("Candidate header is missing or has duplicate columns.")
    frame = pd.read_csv(
        io.BytesIO(payload), dtype=str, keep_default_na=False, skip_blank_lines=False
    )
    if list(frame.columns) != columns:
        raise ValueError("CSV parser did not preserve the declared header.")
    union = sorted({name for qids in qid_sets for name in qids})
    n_out = len(frame)
    reasons: list[str] = []
    current_hash = column_hash(columns)
    missing_qids = sorted(set(union).difference(columns))
    schema_changed = expected_column_hash is not None and current_hash != expected_column_hash
    if schema_changed:
        reasons.append("Delivered columns changed; a new field declaration and review are required.")
    if not union:
        reasons.append("No quasi-identifiers were declared.")
    if missing_qids:
        reasons.append("One or more declared quasi-identifiers are absent from the delivery.")
    if n_out > n_in:
        reasons.append("Delivered row count exceeds the declared source input count.")
    retention = n_out / n_in if n_in else 0.0
    if n_out == 0 or n_in == 0 or retention < minimum_retention:
        reasons.append("Insufficient coverage, including an empty delivery; withhold or use controlled access.")

    minimum_group = None
    groups_below = None
    records_below = None
    singletons = None
    group_count = None
    if union and not missing_qids:
        # Tagged values avoid collision between a missing category and any
        # literal text value (including a literal '<MISSING>' string).
        grouped_fields = pd.DataFrame(index=frame.index)
        for name in union:
            grouped_fields[name] = frame[name].map(
                lambda value: ("missing",) if not value.strip() else ("value", value.strip())
            )
        sizes = grouped_fields.groupby(union, dropna=False).size()
        group_count = len(sizes)
        minimum_group = int(sizes.min()) if len(sizes) else 0
        groups_below = int(sizes.lt(k).sum())
        records_below = int(sizes[sizes.lt(k)].sum())
        singletons = int(sizes[sizes.eq(1)].sum())
        if groups_below:
            reasons.append("The union of declared delivered quasi-identifiers has groups below k.")
    passed = not reasons
    return {
        "snapshot_id": snapshot_id,
        "code_version": "sha256:" + hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "candidate_sha256": hashlib.sha256(payload).hexdigest(),
        "parameters": {
            "k": k, "declared_qid_sets": qid_sets, "delivered_qid_union": union,
            "minimum_retention": minimum_retention,
            "expected_column_hash": expected_column_hash,
            "missing_values": "Blank/whitespace fields are an explicit tagged category; no rows are dropped.",
        },
        "n_in": n_in,
        "n_out": n_out,
        "record_retention": retention,
        "columns": columns,
        "column_sha256": current_hash,
        "column_review_required": schema_changed,
        "group_count": group_count,
        "minimum_group_size": minimum_group,
        "groups_below_k": groups_below,
        "records_below_k": records_below,
        "singleton_count": singletons,
        "automated_decision": "PASS" if passed else "FAIL",
        "reasons": reasons if reasons else ["Declared group-size and coverage checks passed; human authorization is still required."],
        "human_authorization": {"approved_by": None, "approved_at": None, "decision": None},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--qid-set", action="append", nargs="+", required=True)
    parser.add_argument("--n-in", type=int, required=True)
    parser.add_argument("--snapshot-id", required=True)
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--minimum-retention", type=float, default=0.0)
    parser.add_argument("--expected-column-hash")
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    try:
        audit = check_candidate(
            args.candidate, qid_sets=args.qid_set, n_in=args.n_in,
            snapshot_id=args.snapshot_id, k=args.k,
            minimum_retention=args.minimum_retention,
            expected_column_hash=args.expected_column_hash,
        )
    except (ValueError, UnicodeError, pd.errors.ParserError):
        parser.exit(2, "FAIL: candidate format or parameters require review.\n")
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    args.audit.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"automated_decision": audit["automated_decision"],
                      "n_out": audit["n_out"], "groups_below_k": audit["groups_below_k"]}))
    return 0 if audit["automated_decision"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
