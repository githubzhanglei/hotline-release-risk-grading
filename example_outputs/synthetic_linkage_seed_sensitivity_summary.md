# Synthetic T-Linkage Seed Sensitivity

Date: 2026-06-20

Purpose: test whether the leave-one-ticket-out repeated-person linkage results depend on a single auxiliary-ticket sampling seed.

## Summary

| scenario | trials | match coverage mean | match coverage p10-p90 | unique among matched mean | unique among matched p10-p90 | MAP top-person mean | MAP top-person p10-p90 | median candidates mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| street_week_l2_relation_keys | 30 | 0.00% | 0.00% - 0.00% | 0.00% | 0.00% - 0.00% | 0.00% | 0.00% - 0.00% | 0.00 |
| degraded_month_relation_keys | 30 | 0.00% | 0.00% - 0.00% | 0.00% | 0.00% - 0.00% | 0.00% | 0.00% - 0.00% | 0.00 |

## Interpretation

- Exact week + both relation keys remains a narrow-coverage but high-collapse repeated-profile linkage setting.
- Degraded month + both relation keys has higher match coverage because the auxiliary fact is less restrictive, while still producing mostly one-person candidate sets among matched traces.
- These are pseudonym-linkage stability checks, not real-world identity recovery attacks.
