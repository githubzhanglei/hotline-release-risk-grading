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
  public_311_boundary_note.md               # why public 311 scripts are not in this v1 package
  security_scan_report_20260620.md          # local leak-scan record
  release_manifest_20260620.md              # file inventory and checksums
scripts/
  make_synthetic_sample.py
  analyze_privacy_reidentification_risk.py
  evaluate_standard_anonymization_baselines.py
  evaluate_relation_key_release_controls.py
  simulate_synthetic_linkage_attack.py
  evaluate_synthetic_linkage_seed_sensitivity.py
  privacy_utils.py
requirements.txt
```

## Quick Start

Create an environment with Python 3.10 or later, then install the small dependency set:

```bash
pip install -r requirements.txt
```

Regenerate the synthetic sample:

```bash
python scripts/make_synthetic_sample.py
```

Run the aggregate metric and comparator scripts:

```bash
python scripts/analyze_privacy_reidentification_risk.py --skip-stylometry
python scripts/evaluate_standard_anonymization_baselines.py
python scripts/evaluate_relation_key_release_controls.py
python scripts/simulate_synthetic_linkage_attack.py
python scripts/evaluate_synthetic_linkage_seed_sensitivity.py
```

All commands write aggregate-only outputs to `example_outputs/`.

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

It does not reproduce the manuscript's restricted-corpus values because the original 12345 records cannot be redistributed.

## Restricted Data Boundary

The manuscript's local corpus contains sensitive municipal-service records and is not part of this repository. The public package therefore excludes:

- raw 12345 tickets;
- individual complaint narratives;
- real stable address keys;
- real text-derived place keys;
- raw or row-level candidate sets;
- internal experiment-round scripts and process logs.

Only synthetic rows and aggregate example outputs are included.

## Public 311 / Open311 Checks

The manuscript also reports adjacent portability checks on public 311/Open311-style data. The original local workspace contains many exploratory and round-specific public-data scripts. To avoid publishing process traces, this v1 reproducibility package does not include those scripts. The corresponding public-data logic is summarized in `metadata/public_311_boundary_note.md`. A clean standalone public-311 checker can be added in a later release if needed.

## License

No open-source license has been selected yet. Until the author adds a formal license file, the materials are provided for scholarly inspection and reproducibility review only.

## Citation

If citing this package, use the manuscript title above and the repository URL assigned by the author.
