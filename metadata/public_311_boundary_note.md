# Public 311 / Open311 Boundary Note

The manuscript includes adjacent portability checks using public 311/Open311-style fields from large-city open-data portals. Those checks are conceptually separate from the restricted local 12345 corpus.

This repository includes a clean public-data demo:

```bash
python scripts/evaluate_public_311_demo.py
```

The demo fetches a small fixed-window sample from the NYC 311 public API, maps common fields such as date, area, service type, status, and public location surrogate, and computes aggregate structural metrics. It writes:

- `example_outputs/public_311_nyc_structural_demo.csv`
- `example_outputs/public_311_nyc_structural_demo_summary.md`

The script does not write raw 311 rows, raw addresses, or row-level candidate lists.

The local workspace also contains many exploratory and round-specific public-311 scripts. Those files are intentionally excluded because they contain process traces and are not needed for a clean reproducibility package.
