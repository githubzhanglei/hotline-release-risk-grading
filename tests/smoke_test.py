"""Smoke tests for the public reproducibility package."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_OFFLINE_OUTPUTS = [
    "data_sample/synthetic_hotline_sample.csv",
    "example_outputs/k_anonymity_full_sweep.csv",
    "example_outputs/standard_anonymization_ladder.csv",
    "example_outputs/relation_key_release_control_sweep.csv",
    "example_outputs/synthetic_linkage_simulation.csv",
    "example_outputs/synthetic_linkage_seed_sensitivity.csv",
]

EXPECTED_PUBLIC_311_OUTPUTS = [
    "example_outputs/public_311_nyc_structural_demo.csv",
    "example_outputs/public_311_nyc_structural_demo_summary.md",
]


def run(args: list[str]) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def assert_exists(paths: list[str]) -> None:
    missing = [path for path in paths if not (ROOT / path).exists()]
    if missing:
        raise AssertionError("Missing expected outputs: " + ", ".join(missing))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-public-311", action="store_true")
    args = parser.parse_args()

    run(["scripts/run_all_demo.py"] + (["--include-public-311"] if args.include_public_311 else []))
    assert_exists(EXPECTED_OFFLINE_OUTPUTS)
    if args.include_public_311:
        assert_exists(EXPECTED_PUBLIC_311_OUTPUTS)
    print("Smoke test passed.")


if __name__ == "__main__":
    main()
