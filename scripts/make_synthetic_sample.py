"""Generate a fully synthetic municipal-service sample dataset.

The output preserves only the *field structure* used by the analysis scripts in
this repository (column names, value domains, presence rates, recurrence
patterns). It contains NO real records: every district, street, topic, person
key, address key, text-place key, and complaint text is fabricated by this
script from a fixed random seed.

The synthetic sample lets reviewers run the metric/baseline/linkage scripts
end to end without access to the restricted local corpus. It is NOT the data
used in the paper and reproduces no real values or magnitudes.

Usage:
    python scripts/make_synthetic_sample.py
    python scripts/make_synthetic_sample.py --rows 600 --seed 123
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def build(rows: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    districts = ["甲区", "乙区", "丙区"]
    streets = [f"{d}-街道{i}" for d in districts for i in range(1, 4)]
    l1_topics = ["主题大类1", "主题大类2", "主题大类3", "主题大类4"]
    l2_topics = [f"主题小类{a}-{b}" for a in range(1, 5) for b in range(1, 3)]
    units = [f"承办单位{c}" for c in "ABCDE"]
    place_types = [f"地点类型{i}" for i in range(1, 6)]
    subject_types = [f"主体类型{i}" for i in range(1, 5)]
    yes_no = ["是", "否"]

    # Pseudonymous pools. Skewed weights create repeated contributors so that
    # recurrence and uniqueness metrics are non-trivial on the demo data.
    persons = [f"P{i:05d}" for i in range(1, 251)]
    person_w = 1.0 / np.arange(1, len(persons) + 1) ** 0.6
    person_w /= person_w.sum()

    addresses = [f"A{i:05d}" for i in range(1, 121)]
    address_w = 1.0 / np.arange(1, len(addresses) + 1) ** 0.5
    address_w /= address_w.sum()

    text_places = [f"TP{i:05d}" for i in range(1, 201)]
    text_subjects = [f"TS{i:05d}" for i in range(1, 151)]

    start = np.datetime64("2024-03-04")
    records = []
    for i in range(rows):
        district = str(rng.choice(districts))
        street = str(rng.choice([s for s in streets if s.startswith(district)]))
        day = start + np.timedelta64(int(rng.integers(0, 74)), "D")

        person = str(rng.choice(persons, p=person_w)) if rng.random() < 0.86 else ""
        has_addr = rng.random() < 0.95
        address = str(rng.choice(addresses, p=address_w)) if has_addr else ""
        has_tp = rng.random() < 0.90
        text_place = str(rng.choice(text_places)) if has_tp else ""
        has_ts = rng.random() < 0.85
        text_subject = str(rng.choice(text_subjects)) if has_ts else ""

        l2 = str(rng.choice(l2_topics))
        l1 = l1_topics[l2_topics.index(l2) // 2]

        records.append(
            {
                "sample_id": i + 1,
                "ticket_date": np.datetime_as_string(day, unit="D"),
                "person_id": person,
                "区县地址": district,
                "街道地址": street,
                "mapped_l1_name": l1,
                "mapped_l2_name": l2,
                "是否回访": str(rng.choice(yes_no)),
                "问题是否解决": str(rng.choice(yes_no)),
                "是否热点": str(rng.choice(yes_no, p=[0.2, 0.8])),
                "承办单位": str(rng.choice(units)),
                "text_subject_id": text_subject,
                "text_subject_type": str(rng.choice(subject_types)) if has_ts else "",
                "text_place_id": text_place,
                "text_place_type": str(rng.choice(place_types)) if has_tp else "",
                "address_id": address,
                "has_address_id": int(has_addr),
                "has_text_place_id": int(has_tp),
                "has_text_subject_id": int(has_ts),
                "sanitized_text": (
                    "这是合成样例文本，仅用于演示去标识化风险流程，不含任何真实诉求信息。"
                    f"样例主题：{l2}，样例编号：{i + 1:04d}。"
                ),
            }
        )

    df = pd.DataFrame(records)
    person_counts = df.loc[df["person_id"].ne(""), "person_id"].value_counts()
    df["person_total_complaints"] = df["person_id"].map(
        lambda x: int(person_counts.get(x, 0)) if x else 0
    )
    address_counts = df.loc[df["address_id"].ne(""), "address_id"].value_counts()
    df["address_total_complaints"] = df["address_id"].map(
        lambda x: int(address_counts.get(x, 0)) if x else 0
    )
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=Path("data_sample/synthetic_hotline_sample.csv")
    )
    parser.add_argument("--rows", type=int, default=400)
    parser.add_argument("--seed", type=int, default=20260620)
    args = parser.parse_args()

    df = build(args.rows, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(df)} synthetic rows ({df.shape[1]} columns) to {args.output}")


if __name__ == "__main__":
    main()
