# Paper-to-Repository Mapping

This table links the manuscript components to the public repository artifacts. Restricted-corpus values in the manuscript cannot be exactly reproduced from this repository because the original Chinese 12345 corpus cannot be redistributed. The public repository instead supports workflow inspection, script execution, and aggregate-only demonstrations.

| Manuscript component | Repository script | Public input | Public output |
|---|---|---|---|
| Structural metric workflow: k=1 uniqueness, MAP linkage, entropy diagnostics | `scripts/analyze_privacy_reidentification_risk.py` | `data_sample/synthetic_hotline_sample.csv` | `example_outputs/k_anonymity_full_sweep.csv`, `example_outputs/privacy_risk_summary.md` |
| Standard anonymization comparators | `scripts/evaluate_standard_anonymization_baselines.py` | `data_sample/synthetic_hotline_sample.csv` | `example_outputs/standard_anonymization_ladder.csv`, `example_outputs/standard_anonymization_ladder_summary.md` |
| Relation-key suppression and generalization controls | `scripts/evaluate_relation_key_release_controls.py` | `data_sample/synthetic_hotline_sample.csv` | `example_outputs/relation_key_release_control_sweep.csv`, `example_outputs/relation_key_release_control_summary.md` |
| Synthetic auxiliary-linkage demonstration | `scripts/simulate_synthetic_linkage_attack.py` | `data_sample/synthetic_hotline_sample.csv` | `example_outputs/synthetic_linkage_simulation.csv`, `example_outputs/synthetic_linkage_simulation_summary.md` |
| Seed-sensitivity check for synthetic linkage | `scripts/evaluate_synthetic_linkage_seed_sensitivity.py` | `data_sample/synthetic_hotline_sample.csv` | `example_outputs/synthetic_linkage_seed_sensitivity.csv`, `example_outputs/synthetic_linkage_seed_sensitivity_summary.md` |
| Public 311 adjacent portability demo | `scripts/evaluate_public_311_demo.py` | NYC 311 public API, fixed query window | `example_outputs/public_311_nyc_structural_demo.csv`, `example_outputs/public_311_nyc_structural_demo_summary.md` |
| End-to-end offline workflow | `scripts/run_all_demo.py` | synthetic sample generator | all offline `example_outputs/` artifacts |
| Smoke test | `tests/smoke_test.py` | synthetic sample generator, optional NYC 311 API | output existence checks |

The public 311 demo uses public records but stores only aggregate outputs. No raw public 311 rows or addresses are committed.
