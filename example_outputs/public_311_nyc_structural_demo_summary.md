# Public 311 Structural Demo Summary

Source: NYC 311 public API.
Window: `2024-02-01T00:00:00` to `2024-02-08T00:00:00`.

The script writes aggregate metrics only. It does not save raw 311 rows, addresses, or row-level candidate lists.

| Scenario | Records | Locations | k=1 uniqueness | MAP location linkage | Effective location candidates |
|---|---:|---:|---:|---:|---:|
| citywide | 1000 | 782 | 0.00% | 2.70% | 658.78 |
| borough_week_type | 1000 | 782 | 5.90% | 23.60% | 12.03 |
| zip_week_type | 1000 | 782 | 38.20% | 71.30% | 1.71 |
| zip_week_type_status | 1000 | 782 | 38.20% | 71.30% | 1.71 |
| zip_day_type_descriptor | 1000 | 782 | 56.20% | 81.70% | 1.39 |
| relation_key_released | 1000 | 782 | 75.80% | 100.00% | 1.00 |

Source query URL is stored for provenance but no source rows are stored.

`https://data.cityofnewyork.us/resource/erm2-nwe9.json?%24limit=1000&%24select=created_date%2Cagency%2Ccomplaint_type%2Cdescriptor%2Cincident_zip%2Cborough%2Cincident_address%2Cstatus&%24where=created_date+between+%272024-02-01T00%3A00%3A00%27+and+%272024-02-08T00%3A00%3A00%27+AND+incident_address+IS+NOT+NULL&%24order=created_date+ASC`
