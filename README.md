# Privacy-Risk Engineering Reproducibility Package

This repository contains a public, non-sensitive reproducibility package for:

**Privacy-Risk Engineering for Secure Municipal Service Data Release: Structural Linkage Grading and Comparative Controls**

The restricted Chinese 12345 municipal-service corpus used in the manuscript is **not** included. This package provides:

- metric and comparator scripts used by the manuscript workflow;
- a deterministic synthetic municipal-service sample with the same field structure;
- aggregate-only example outputs generated from the synthetic sample;
- metadata describing the reproducibility boundary and public-release safety scan.

The synthetic sample is not a substitute for the restricted corpus and will not reproduce the paper's numeric findings. It is designed to let reviewers inspect and run the metric pipeline end to end without exposing any real record, complaint text, address key, person key, or text-derived place key.

## Repository Layout

```text
data_sample/
  synthetic_hotline_sample.csv              # 400 fully synthetic rows
example_outputs/
  *.csv, *.md                               # outputs regenerated from the synthetic sample
metadata/
  data_schema.md                            # field-level schema notes
  paper_artifact_mapping.md                 # manuscript-to-script/output mapping
  public_311_boundary_note.md               # public 311 demo boundary
  security_scan_report_20260620.md          # local leak-scan record
  release_manifest_20260620.md              # file inventory and checksums
scripts/
  run_all_demo.py
  make_synthetic_sample.py
  analyze_privacy_reidentification_risk.py
  evaluate_standard_anonymization_baselines.py
  evaluate_relation_key_release_controls.py
  evaluate_public_311_demo.py
  simulate_synthetic_linkage_attack.py
  evaluate_synthetic_linkage_seed_sensitivity.py
  privacy_utils.py
tests/
  smoke_test.py
requirements.txt
```

## Quick Start

Create an environment with Python 3.10 or later, then install the small dependency set:

```bash
pip install -r requirements.txt
```

Run the offline synthetic-data workflow:

```bash
python scripts/run_all_demo.py
```

Run a smoke test for the same workflow:

```bash
python tests/smoke_test.py
```

All commands write aggregate-only outputs to `example_outputs/`.

Optionally run the public NYC 311 demo. This step uses the NYC open-data API and writes aggregate metrics only:

```bash
python scripts/evaluate_public_311_demo.py
```

Or include it in the one-command demo:

```bash
python scripts/run_all_demo.py --include-public-311
```

## What This Package Can Reproduce

This package reproduces the **workflow mechanics**:

- quasi-identifier grouping;
- k=1 uniqueness;
- MAP pseudonym linkage;
- entropy-based diagnostics;
- k-anonymity and person-diversity comparator summaries;
- relation-key suppression/generalization controls;
- synthetic auxiliary-fact linkage simulation;
- deterministic seed-sensitivity checks.
- an aggregate-only public NYC 311 structural demo.

It does not reproduce the manuscript's restricted-corpus values because the original 12345 records cannot be redistributed.

For a paper-to-repository mapping, see `metadata/paper_artifact_mapping.md`.

## Restricted Data Boundary

The manuscript's local corpus contains sensitive municipal-service records and is not part of this repository. The public package therefore excludes:

- raw 12345 tickets;
- individual complaint narratives;
- real stable address keys;
- real text-derived place keys;
- raw or row-level candidate sets;
- internal experiment-round scripts and process logs.

Only synthetic rows and aggregate example outputs are included.

## Public 311 / Open311 Demo

The manuscript also reports adjacent portability checks on public 311/Open311-style data. This repository includes a clean public NYC 311 demo in `scripts/evaluate_public_311_demo.py`.

The demo fetches a small fixed-window sample from the NYC 311 public API, computes structural grouping metrics, and exports only aggregate tables. It does not store raw 311 rows, addresses, or row-level candidate lists. The historical exploratory public-311 scripts from the local workspace are intentionally excluded.

## License

No open-source license has been selected yet. Until the author adds a formal license file, the materials are provided for scholarly inspection and reproducibility review only.

## Citation

If citing this package, use the manuscript title above and the repository URL assigned by the author.
