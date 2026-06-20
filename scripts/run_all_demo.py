"""Run the reproducibility package demo commands.

By default this script runs the offline synthetic-data workflow only. Add
`--include-public-311` to also fetch a small public NYC 311 sample and write
aggregate-only public-data metrics.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


OFFLINE_COMMANDS = [
    ["scripts/make_synthetic_sample.py"],
    ["scripts/analyze_privacy_reidentification_risk.py", "--skip-stylometry"],
    ["scripts/evaluate_standard_anonymization_baselines.py"],
    ["scripts/evaluate_relation_key_release_controls.py"],
    ["scripts/simulate_synthetic_linkage_attack.py"],
    ["scripts/evaluate_synthetic_linkage_seed_sensitivity.py"],
]


def run(script_args: list[str]) -> None:
    command = [sys.executable, *script_args]
    print("$ " + " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-public-311",
        action="store_true",
        help="Also run the networked public NYC 311 aggregate demo.",
    )
    args = parser.parse_args()

    for command in OFFLINE_COMMANDS:
        run(command)

    if args.include_public_311:
        run(["scripts/evaluate_public_311_demo.py"])

    print("Demo complete.")


if __name__ == "__main__":
    main()
