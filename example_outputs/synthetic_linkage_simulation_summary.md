# Safe Synthetic T-Linkage Simulation

Date: 2026-06-20

No external identity-bearing data are used. Each auxiliary row is a synthetic known-fact record sampled from one pseudonymous person's ticket history.
The result quantifies joinability and candidate-set collapse, not real-world legal identity recovery.

## Results

| scenario | scenario_type | matched_aux_persons | match_coverage | target_still_candidate_coverage | pct_unique_candidate_person | pct_candidate_persons_le_5 | median_candidate_persons | mean_candidate_persons | map_top_person_success | random_within_candidates_success |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| street_topic_no_week | exact_auxiliary__same_row_included | 143 | 100.0 | 100.0 | 1.4 | 57.34 | 5.0 | 5.36 | 25.87 | 22.47 |
| street_topic_no_week | exact_auxiliary__leave_one_ticket_out_all | 141 | 98.6 | 2.13 | 5.67 | 74.47 | 4.0 | 4.44 | 2.13 | 0.5 |
| street_topic_no_week | exact_auxiliary__leave_one_ticket_out_repeated | 73 | 97.33 | 4.11 | 4.11 | 73.97 | 4.0 | 4.45 | 4.11 | 0.96 |
| street_week_l1 | exact_auxiliary__same_row_included | 143 | 100.0 | 100.0 | 39.86 | 100.0 | 2.0 | 1.86 | 67.83 | 66.2 |
| street_week_l1 | exact_auxiliary__leave_one_ticket_out_all | 86 | 60.14 | 0.0 | 68.6 | 100.0 | 1.0 | 1.43 | 0.0 | 0.0 |
| street_week_l1 | exact_auxiliary__leave_one_ticket_out_repeated | 44 | 58.67 | 0.0 | 70.45 | 100.0 | 1.0 | 1.43 | 0.0 | 0.0 |
| street_week_l2 | exact_auxiliary__same_row_included | 143 | 100.0 | 100.0 | 69.23 | 100.0 | 1.0 | 1.34 | 86.71 | 84.03 |
| street_week_l2 | exact_auxiliary__leave_one_ticket_out_all | 44 | 30.77 | 0.0 | 88.64 | 100.0 | 1.0 | 1.11 | 0.0 | 0.0 |
| street_week_l2 | exact_auxiliary__leave_one_ticket_out_repeated | 20 | 26.67 | 0.0 | 85.0 | 100.0 | 1.0 | 1.15 | 0.0 | 0.0 |
| street_week_l2_process | exact_auxiliary__same_row_included | 143 | 100.0 | 100.0 | 88.11 | 100.0 | 1.0 | 1.13 | 95.1 | 93.82 |
| street_week_l2_process | exact_auxiliary__leave_one_ticket_out_all | 17 | 11.89 | 0.0 | 88.24 | 100.0 | 1.0 | 1.12 | 0.0 | 0.0 |
| street_week_l2_process | exact_auxiliary__leave_one_ticket_out_repeated | 8 | 10.67 | 0.0 | 75.0 | 100.0 | 1.0 | 1.25 | 0.0 | 0.0 |
| street_week_l2_place_type | exact_auxiliary__same_row_included | 143 | 100.0 | 100.0 | 97.9 | 100.0 | 1.0 | 1.03 | 98.6 | 98.83 |
| street_week_l2_place_type | exact_auxiliary__leave_one_ticket_out_all | 3 | 2.1 | 0.0 | 66.67 | 100.0 | 1.0 | 1.33 | 0.0 | 0.0 |
| street_week_l2_place_type | exact_auxiliary__leave_one_ticket_out_repeated | 1 | 1.33 | 0.0 | 100.0 | 100.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| street_week_l2_subject_type | exact_auxiliary__same_row_included | 143 | 100.0 | 100.0 | 93.01 | 100.0 | 1.0 | 1.07 | 97.9 | 96.5 |
| street_week_l2_subject_type | exact_auxiliary__leave_one_ticket_out_all | 10 | 6.99 | 0.0 | 100.0 | 100.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| street_week_l2_subject_type | exact_auxiliary__leave_one_ticket_out_repeated | 5 | 6.67 | 0.0 | 100.0 | 100.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| street_week_l2_text_place_id | exact_auxiliary__same_row_included | 143 | 100.0 | 100.0 | 100.0 | 100.0 | 1.0 | 1.0 | 100.0 | 100.0 |
| street_week_l2_text_place_id | exact_auxiliary__leave_one_ticket_out_all | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| street_week_l2_text_place_id | exact_auxiliary__leave_one_ticket_out_repeated | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| street_week_l2_address_id | exact_auxiliary__same_row_included | 143 | 100.0 | 100.0 | 100.0 | 100.0 | 1.0 | 1.0 | 100.0 | 100.0 |
| street_week_l2_address_id | exact_auxiliary__leave_one_ticket_out_all | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| street_week_l2_address_id | exact_auxiliary__leave_one_ticket_out_repeated | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| street_week_l2_relation_keys | exact_auxiliary__same_row_included | 143 | 100.0 | 100.0 | 100.0 | 100.0 | 1.0 | 1.0 | 100.0 | 100.0 |
| street_week_l2_relation_keys | exact_auxiliary__leave_one_ticket_out_all | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| street_week_l2_relation_keys | exact_auxiliary__leave_one_ticket_out_repeated | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| degraded_no_week_text_place_id | degraded_auxiliary__same_row_included | 143 | 100.0 | 100.0 | 91.61 | 100.0 | 1.0 | 1.1 | 97.2 | 95.57 |
| degraded_no_week_text_place_id | degraded_auxiliary__leave_one_ticket_out_all | 12 | 8.39 | 0.0 | 83.33 | 100.0 | 1.0 | 1.17 | 0.0 | 0.0 |
| degraded_no_week_text_place_id | degraded_auxiliary__leave_one_ticket_out_repeated | 8 | 10.67 | 0.0 | 75.0 | 100.0 | 1.0 | 1.25 | 0.0 | 0.0 |
| degraded_month_text_place_id | degraded_auxiliary__same_row_included | 143 | 100.0 | 100.0 | 99.3 | 100.0 | 1.0 | 1.01 | 100.0 | 99.65 |
| degraded_month_text_place_id | degraded_auxiliary__leave_one_ticket_out_all | 1 | 0.7 | 0.0 | 100.0 | 100.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| degraded_month_text_place_id | degraded_auxiliary__leave_one_ticket_out_repeated | 1 | 1.33 | 0.0 | 100.0 | 100.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| degraded_l1_week_text_place_id | degraded_auxiliary__same_row_included | 143 | 100.0 | 100.0 | 99.3 | 100.0 | 1.0 | 1.01 | 100.0 | 99.65 |
| degraded_l1_week_text_place_id | degraded_auxiliary__leave_one_ticket_out_all | 1 | 0.7 | 0.0 | 100.0 | 100.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| degraded_l1_week_text_place_id | degraded_auxiliary__leave_one_ticket_out_repeated | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| degraded_no_week_address_id | degraded_auxiliary__same_row_included | 143 | 100.0 | 100.0 | 93.71 | 100.0 | 1.0 | 1.06 | 97.2 | 96.85 |
| degraded_no_week_address_id | degraded_auxiliary__leave_one_ticket_out_all | 9 | 6.29 | 0.0 | 100.0 | 100.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| degraded_no_week_address_id | degraded_auxiliary__leave_one_ticket_out_repeated | 5 | 6.67 | 0.0 | 100.0 | 100.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| degraded_month_address_id | degraded_auxiliary__same_row_included | 143 | 100.0 | 100.0 | 94.41 | 100.0 | 1.0 | 1.06 | 97.9 | 97.2 |
| degraded_month_address_id | degraded_auxiliary__leave_one_ticket_out_all | 8 | 5.59 | 0.0 | 100.0 | 100.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| degraded_month_address_id | degraded_auxiliary__leave_one_ticket_out_repeated | 4 | 5.33 | 0.0 | 100.0 | 100.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| degraded_month_relation_keys | degraded_auxiliary__same_row_included | 143 | 100.0 | 100.0 | 100.0 | 100.0 | 1.0 | 1.0 | 100.0 | 100.0 |
| degraded_month_relation_keys | degraded_auxiliary__leave_one_ticket_out_all | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| degraded_month_relation_keys | degraded_auxiliary__leave_one_ticket_out_repeated | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Interpretation Boundary

- This is a controlled joinability proxy for T-Linkage.
- Degraded auxiliary scenarios remove week precision or lower topic precision so the result is not only an exact same-row upper bound.
- Leave-one-ticket-out scenarios remove the synthetic auxiliary ticket from the release table before joining.
- It should not be described as an attack on real citizens.
- Strong results under `address_id` and `text_place_id` mean those fields create small candidate sets when an adversary has matching facts.
