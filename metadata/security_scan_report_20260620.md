# Public-Release Safety Scan Report

Date: 2026-06-20

Scope: `release_repo/`

## Included Materials

- 9 Python files under `scripts/`
- 1 smoke-test file under `tests/`
- 1 synthetic sample CSV under `data_sample/`
- aggregate example outputs under `example_outputs/`
- metadata and README files

## Safety Boundary

The package intentionally excludes:

- raw local 12345 records;
- row-level restricted-corpus outputs;
- real address keys or text-place keys;
- real complaint narratives;
- internal round scripts and development logs;
- raw public 311 rows or addresses;
- submission packages and manuscript build artifacts.

## Commands Run

Syntax check:

```bash
python -m py_compile scripts/privacy_utils.py scripts/make_synthetic_sample.py scripts/analyze_privacy_reidentification_risk.py scripts/evaluate_standard_anonymization_baselines.py scripts/evaluate_relation_key_release_controls.py scripts/simulate_synthetic_linkage_attack.py scripts/evaluate_synthetic_linkage_seed_sensitivity.py
```

Demo run:

```bash
python scripts/make_synthetic_sample.py
python scripts/analyze_privacy_reidentification_risk.py --skip-stylometry
python scripts/evaluate_standard_anonymization_baselines.py
python scripts/evaluate_relation_key_release_controls.py
python scripts/simulate_synthetic_linkage_attack.py
python scripts/evaluate_synthetic_linkage_seed_sensitivity.py
python scripts/evaluate_public_311_demo.py
python tests/smoke_test.py
python tests/smoke_test.py --include-public-311
```

Pattern scan:

The package was scanned for real-data filenames, absolute local paths, internal round labels, previous-venue names, submission-package markers, author-template placeholders, and process-log phrases.

## Result

No hits were found for real-data paths, absolute local paths, old submission packages, internal round labels, old journal names, author-template placeholders, or process-log phrases.

The only matches for Chinese words such as "真实" or "敏感" occur in explicit synthetic-data disclaimers, for example "不含任何真实诉求信息".

The public 311 script writes only aggregate outputs:

- `example_outputs/public_311_nyc_structural_demo.csv`
- `example_outputs/public_311_nyc_structural_demo_summary.md`

No raw 311 row file is committed.

## Residual Items for Author Decision

- Add the final GitHub repository URL after the repository is created.
- Choose whether to add a formal open-source license. No license has been selected in this package.
- Decide whether a later release should add more cities to the clean public-311 checker.
