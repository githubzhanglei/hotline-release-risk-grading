# Release Manifest

Date: 2026-06-20

Package root: `release_repo/`

This manifest records the public reproducibility package assembled for scholarly review. It is not a journal upload manifest.

## Core Files

| Path | Role |
|---|---|
| `README.md` | Repository overview and run instructions |
| `requirements.txt` | Minimal Python dependencies |
| `.gitignore` | Cache and build-output exclusions |
| `data_sample/synthetic_hotline_sample.csv` | Fully synthetic sample dataset |
| `scripts/make_synthetic_sample.py` | Deterministic synthetic sample generator |
| `scripts/privacy_utils.py` | Shared date utilities |
| `scripts/analyze_privacy_reidentification_risk.py` | Structural metric audit |
| `scripts/evaluate_standard_anonymization_baselines.py` | Standard anonymization comparators |
| `scripts/evaluate_relation_key_release_controls.py` | Relation-key release controls |
| `scripts/simulate_synthetic_linkage_attack.py` | Synthetic auxiliary-linkage simulation |
| `scripts/evaluate_synthetic_linkage_seed_sensitivity.py` | Seed-sensitivity check |
| `example_outputs/*` | Aggregate outputs regenerated from the synthetic sample |
| `metadata/data_schema.md` | Synthetic sample schema |
| `metadata/public_311_boundary_note.md` | Public-311 reproducibility boundary |
| `metadata/security_scan_report_20260620.md` | Public-release safety scan |
| `metadata/github_push_commands.md` | Local push commands for creating the public repository |

## Excluded From This Release

- restricted local corpus;
- raw text or row-level candidate records;
- internal experiment-round scripts;
- manuscript source packages;
- journal submission files;
- Python cache files.

## Checksums

SHA256 values below exclude this manifest file itself.

```text
2bf352b5039e1f316a5ca1e908403e99dada3b95bf95eea13b59f9d528191587  .gitignore
cc8c184c25b6600dbd468ff2da1358c1ad367452440d63d927a2617d1fe1bcb7  CITATION.cff
84545171355925753c693d2fa48c584d6dbf9fcccdcbdd53ba10d71d65a10c6d  data_sample/synthetic_hotline_sample.csv
9c2ae90c0ba3d0c65772da51de951b40eb5deb153bcb3e013f13eb6f66cf5ec9  example_outputs/k_anonymity_full_sweep.csv
92c2af08d60ef14d58c1d4208570038ea2cfe86624063f50ef1216479c9ec185  example_outputs/nstar_sensitivity.csv
b4a2e6af1191f322e3f9014947f19786a404074f3959f6ab51a17a338956d308  example_outputs/person_recurrence_distribution.csv
2166e0f87c2e010a51b00da96c8c1c62027248cd9a982e21cd49bad78a432ba8  example_outputs/privacy_risk_summary.md
3488e317dbc556f130bf68ca52dc7411a673bf42a26cb65d531e7a2a49d7005e  example_outputs/relation_key_release_control_summary.md
c7f4051941e2cd8b537639c341657bda459d6ea62f73e3a435572750fd7b70d3  example_outputs/relation_key_release_control_sweep.csv
e78f3bbc4af7e8a81bb3883ea39e9d9ded6a6820ccabe937ea5849772d472113  example_outputs/standard_anonymization_ladder.csv
527bc6226c67c4d727d669d325658b48ae45d52c47126b9a333486c0c26dc787  example_outputs/standard_anonymization_ladder_summary.md
9cf489cc87c0e91a2fe7f9865fa6490625c5ec0bf2e1f8df15186cb256297c71  example_outputs/synthetic_linkage_seed_sensitivity.csv
aa78ceecb4cabbe98b3d337064c6e9f0799d56bf585e8d0959ed85327679659a  example_outputs/synthetic_linkage_seed_sensitivity_summary.md
f9d359fa64eb50ec2765ae4acff99b68b9d983f3bb69537e74880542f2a8b380  example_outputs/synthetic_linkage_seed_sensitivity_trials.csv
b5988ef5e656dbd0dabb7792ccaa140d3513ff419c11f374134f779146906364  example_outputs/synthetic_linkage_simulation.csv
138d737b4048e373e37fca7abdb2172bd34cb5052cdc95c36f391bb7de061de6  example_outputs/synthetic_linkage_simulation_summary.md
296266cec9016eeab657a61efe5d92f16c65aa93de569c2adc349b32ff42cf26  LICENSE_PENDING.md
b3db4e2a0f4a714a83af7d4d39a1765e7dd19a5f22bc7435416f49a4e3d2b6c0  metadata/data_schema.md
8b4f5315cdfd971ff4f4a80ffe43810e167f493e0f42b6d4e195df7e87501acd  metadata/github_push_commands.md
1658ba89f8bc70c0289a91a785d9ce509d2b065be39c8f395dd7bbe1b0d1dea2  metadata/public_311_boundary_note.md
1e8a7af77ea66524dcc60a17ca3abbbf0ba8767f772edee47a2e32bf7a53c561  metadata/security_scan_report_20260620.md
b2ce945cb593437b9eca955335c3ed7d5213c5c3ea610fa1a7dd7d58218c1550  README.md
8b47f8b227c7d9bdf0d44670c86a974c397a100e9bfe36565c7b7f689bdfbbcb  requirements.txt
3fda90bacbee106cc6a4ab5d00259c730f76be0a7b86b933d0faf23a2614fe56  scripts/analyze_privacy_reidentification_risk.py
a767287d92b8b89a5acae594ba8881aab91f5501af4733a3f18ee3fdcd39b8f2  scripts/evaluate_relation_key_release_controls.py
a1cf144941808f7d539cc43569266e9bae8c51a41dad850b51dda5ebd3a0e36a  scripts/evaluate_standard_anonymization_baselines.py
d4d302897169f772aba8bbdbcfef0682f1d74d261d95a3389047033a75332808  scripts/evaluate_synthetic_linkage_seed_sensitivity.py
9749c2be17be5e403790693752b8905261bc27c88726588ac194c78f21d4c39f  scripts/make_synthetic_sample.py
fc6db69321403af987066947e5c6b70f95546899702ba44ba7aa1d89f8f80b61  scripts/privacy_utils.py
4cf1151b4404c55c5433336fa7a7c0cac4870192f4e0e672869151255c16673f  scripts/simulate_synthetic_linkage_attack.py
```
