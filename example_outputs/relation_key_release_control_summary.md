# Relation-key Release Control Sweep

Date: 2026-06-20

Privacy unit: pseudonymous `person_id`.
Controls suppress relation-key values whose empirical person-diversity is below a threshold.

## Selected Results

| scenario | control_type | threshold_persons | pct_records_k1 | pct_records_k_le_5 | map_reid_accuracy | i_struct_empirical_bits | effective_person_candidates | delta_k1_vs_topic_only_pp | delta_map_vs_topic_only_pp | release_guidance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| topic_only | baseline | 0 | 67.16 | 100.0 | 82.99 | 6.331 | 1.278 | nan | nan | minimum structural release baseline |
| raw_text_place_id | raw_or_generalized | 0 | 100.0 | 100.0 | 100.0 | 6.685 | 1.0 | 32.845 | 17.009 | raw relation key; unsafe |
| raw_address_id | raw_or_generalized | 0 | 100.0 | 100.0 | 100.0 | 6.685 | 1.0 | 32.845 | 17.009 | raw stable address key; unsafe |
| raw_relation_keys | raw_or_generalized | 0 | 100.0 | 100.0 | 100.0 | 6.685 | 1.0 | 32.845 | 17.009 | raw combined relation keys; unsafe |
| text_place_type_only | raw_or_generalized | 0 | 92.38 | 100.0 | 95.89 | 6.598 | 1.062 | 25.22 | 12.903 | generalize text place key to type |
| presence_flags_only | raw_or_generalized | 0 | 79.47 | 100.0 | 89.74 | 6.475 | 1.156 | 12.317 | 6.745 | release only whether a relation key exists |
| relation_keys_k2 | threshold_suppression | 2 | 100.0 | 100.0 | 100.0 | 6.685 | 1.0 | 32.845 | 17.009 | threshold-suppress both address and text-place keys below person-diversity k |
| relation_keys_k5 | threshold_suppression | 5 | 88.56 | 100.0 | 94.13 | 6.565 | 1.086 | 21.408 | 11.144 | threshold-suppress both address and text-place keys below person-diversity k |
| relation_keys_k10 | threshold_suppression | 10 | 72.14 | 100.0 | 85.63 | 6.386 | 1.23 | 4.985 | 2.639 | threshold-suppress both address and text-place keys below person-diversity k |
| relation_keys_k20 | threshold_suppression | 20 | 67.16 | 100.0 | 82.99 | 6.331 | 1.278 | 0.0 | 0.0 | threshold-suppress both address and text-place keys below person-diversity k |
| relation_keys_k50 | threshold_suppression | 50 | 67.16 | 100.0 | 82.99 | 6.331 | 1.278 | 0.0 | 0.0 | threshold-suppress both address and text-place keys below person-diversity k |

## Current Best Suppression Row

| scenario | control_type | threshold_persons | pct_records_k1 | pct_records_k_le_5 | map_reid_accuracy | i_struct_empirical_bits | effective_person_candidates | delta_k1_vs_topic_only_pp | delta_map_vs_topic_only_pp | release_guidance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| relation_keys_k20 | threshold_suppression | 20 | 67.16 | 100.0 | 82.99 | 6.331 | 1.278 | 0.0 | 0.0 | threshold-suppress both address and text-place keys below person-diversity k |

## Interpretation Boundary

- Suppression thresholds are empirical controls for this snapshot, not formal privacy guarantees.
- Generalizing relation keys to coarse types is safer than releasing raw stable keys, but it does not replace DP for public aggregate release.
- A publishable defense section should combine key suppression/generalization with bounded-contribution DP for released statistics.
