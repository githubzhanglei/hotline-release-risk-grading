# Public 311 / Open311 Boundary Note

The manuscript includes adjacent portability checks using public 311/Open311-style fields from large-city open-data portals. Those checks are conceptually separate from the restricted local 12345 corpus.

This first public reproducibility package does **not** include the local workspace's exploratory public-311 scripts because that workspace contains many round-specific process scripts, intermediate certificates, and development traces. Publishing those files would make the repository harder to audit and could introduce draft-process leakage.

The public-311 component can be reproduced cleanly in a later release with a standalone script that:

1. reads public records from city open-data APIs or downloaded CSV files;
2. maps common fields such as date, administrative area, service category, status, and location surrogate;
3. computes the same aggregate structural metrics used by the main scripts;
4. exports only aggregate tables.

The v1 repository therefore focuses on the restricted-corpus metric workflow, standard anonymization comparators, relation-key controls, and synthetic auxiliary-linkage simulation, all using a fully synthetic sample.
