# ERX Quality-Gate Reference Implementation

Version label: `v1.0.1-erx` (the `v1.0-erx` validator and tests, unchanged, with the MIT license added).

The independent validator is `scripts/quality_gate.py`; its boundary tests are
`tests/test_quality_gate.py`. It reads a delivered structured CSV rather than
calling the generator or trusting its in-memory grouping. All declared
quasi-identifiers present in the delivery are checked together. A declared field
missing from the delivery fails review. Missing/blank field values participate
in grouping through a tagged category that cannot collide with a literal value.

The synthetic audit example is `example_outputs/quality_gate_audit_example.json`.
Its input identifier refers only to the deterministic 400-record synthetic
sample. The code-version field identifies the validator by source SHA256; the
candidate SHA256 and complete column-list hash bind the audit to the delivered
bytes and schema. The declared source row count and minimum retention are inputs
to the check, not quantities certified from a separate source database.

Automatic `PASS` means the declared record-group and coverage checks passed.
Human authorization is recorded separately and remains blank in the example.
No population identity-recovery guarantee or legal release permission follows
from this result. An undeclared quasi-identifier is a declaration failure that
software cannot resolve by itself.

## Reproduction

Use Python 3.10 or later and `requirements.txt`. The validator is deterministic
and has no random seed. Run the two commands under the README's quality-gate
section. The example should report 400 delivered records, no groups below k=5,
and blank human authorization. The complete offline demonstration can be checked
with `python tests/smoke_test.py`; it uses synthetic inputs only.

Restricted-corpus results, bookkeeping counts, raw municipal records, real key
values, and private revision logs are not included. This addition supplies an
inspectable engineering check; it does not reproduce the manuscript's private
numeric results.
