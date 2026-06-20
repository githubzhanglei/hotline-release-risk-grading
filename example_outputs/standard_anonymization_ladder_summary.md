# Standard Anonymization Ladder Baselines

Date: 2026-06-20

Purpose: compare the relation-key controls against conventional recoding and k-anonymity-style row suppression baselines.
Row suppression metrics are evaluated only on retained person records; utility must therefore be read together with retained record percentage.

## Results

| policy | family | suppression_threshold_persons | retained_person_records_pct | pct_records_k1 | map_reid_accuracy | fano_error_lb_uniform | relation_key_detail_retained_proxy_pct | risk_band |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global | recoding | 0 | 100.000 | 0.000 | 5.572 | 86.033 | 0.000 | low-to-moderate |
| district_month_l1 | recoding | 0 | 100.000 | 0.000 | 15.249 | 38.079 | 0.000 | low-to-moderate |
| district_week_l1 | recoding | 0 | 100.000 | 6.158 | 37.243 | 15.716 | 0.000 | moderate |
| street_month_l1 | recoding | 0 | 100.000 | 3.226 | 31.672 | 19.037 | 0.000 | moderate |
| street_month_l2 | recoding | 0 | 100.000 | 18.768 | 50.733 | 8.835 | 0.000 | high |
| street_week_l1 | recoding | 0 | 100.000 | 42.522 | 67.742 | 2.769 | 0.000 | critical |
| street_week_l2 | recoding | 0 | 100.000 | 67.155 | 82.991 | 0.000 | 0.000 | critical |
| street_week_l2_solved | recoding | 0 | 100.000 | 83.284 | 91.202 | 0.000 | 0.000 | critical |
| street_week_l2_presence_flags | coarse_relation_generalization | 0 | 100.000 | 75.073 | 87.097 | 0.000 | 0.000 | critical |
| street_week_l2_place_type | coarse_relation_generalization | 0 | 100.000 | 92.375 | 95.894 | 0.000 | 0.000 | critical |
| street_week_l2_raw_relation_keys | unsafe_raw_relation_keys | 0 | 100.000 | 100.000 | 100.000 | 0.000 | 93.625 | critical |
| topic_qid_row_suppression_k2 | standard_k_anonymity_row_suppression | 2 | 32.258 | 0.000 | 47.273 | 6.569 | 0.000 | high |
| topic_qid_row_suppression_k5 | standard_k_anonymity_row_suppression | 5 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | low-to-moderate |
| topic_qid_row_suppression_k10 | standard_k_anonymity_row_suppression | 10 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | low-to-moderate |
| topic_qid_row_suppression_k20 | standard_k_anonymity_row_suppression | 20 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | low-to-moderate |
| topic_qid_row_suppression_k50 | standard_k_anonymity_row_suppression | 50 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | low-to-moderate |
| raw_relation_qid_row_suppression_k2 | standard_k_anonymity_row_suppression | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | low-to-moderate |
| raw_relation_qid_row_suppression_k5 | standard_k_anonymity_row_suppression | 5 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | low-to-moderate |
| raw_relation_qid_row_suppression_k10 | standard_k_anonymity_row_suppression | 10 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | low-to-moderate |
| raw_relation_qid_row_suppression_k20 | standard_k_anonymity_row_suppression | 20 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | low-to-moderate |
| raw_relation_qid_row_suppression_k50 | standard_k_anonymity_row_suppression | 50 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | low-to-moderate |
| presence_flag_qid_row_suppression_k2 | standard_k_anonymity_row_suppression | 2 | 24.340 | 0.000 | 46.988 | 6.719 | 0.000 | high |
| presence_flag_qid_row_suppression_k5 | standard_k_anonymity_row_suppression | 5 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | low-to-moderate |
| presence_flag_qid_row_suppression_k10 | standard_k_anonymity_row_suppression | 10 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | low-to-moderate |
| presence_flag_qid_row_suppression_k20 | standard_k_anonymity_row_suppression | 20 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | low-to-moderate |
| presence_flag_qid_row_suppression_k50 | standard_k_anonymity_row_suppression | 50 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | low-to-moderate |

## Interpretation

- Coarse recoding lowers linkage risk by reducing geography, time, or topic precision, but also removes much of the monitoring value.
- Standard row suppression can make the retained table safer, but may retain very few records when raw relation keys are included.
- These baselines should be used to avoid claiming that topic-only is the only comparator.
