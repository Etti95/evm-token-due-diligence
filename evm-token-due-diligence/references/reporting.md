# Reporting standard

## Direct verdict first

Answer the user's decision question in the first paragraph with scope and time basis. Make conditions explicit. Then give the main reasons, strongest contrary evidence, unresolved questions, and evidence that would change the result. Recommendations must repair observed deficiencies rather than restate generic best practices.

Do not say “safe.” Use bounded outcomes such as `GO under stated conditions`, `CAUTION`, `NO-GO under stated requirement`, or `UNKNOWN / insufficient evidence`. A favorable control review predicts neither liquidity nor returns.

## Required broad/formal ratings

Rate these independently:

1. token controls;
2. canonical LP-principal custody;
3. side-pool removal risk;
4. sellability and exit depth;
5. current concentration;
6. historical launch integrity;
7. admin, treasury, and reward custody;
8. reward accounting and liveness;
9. utility and redemption rights;
10. external dependencies;
11. development and disclosure.

For every rating provide:

- `severity`: informational, low, medium, high, critical, or unknown;
- `likelihood`: unlikely, possible, likely, active/observed, not_applicable, or unknown;
- `confidence`: high, medium, low, or unknown;
- `coverage`: exact included/excluded contracts, ranges, routes, sizes, and limitations;
- `time_basis`: current pin(s) and any historical transactions/ranges;
- short conclusion plus evidence/finding IDs.

Use `unknown` rather than a favorable rating when evidence is absent. Do not compute or present an average score that can offset a critical finding.

## Layered broad-report shape

1. Exact target, mode, decision rule, and pins.
2. Conditional verdict.
3. Critical/high findings and strongest contrary evidence.
4. Separate ratings table.
5. Architecture/control map.
6. Liquidity custody and executable-depth tests.
7. supply/current concentration and launch history.
8. fees/treasury/rewards/redemption and dependency analysis.
9. unresolved questions, coverage failures, and stale conditions.
10. recommendations tied to findings.
11. finding-to-evidence ledger and artifact/query index.

Focused answers may be much shorter but retain exact target, pin, evidence class, limits, and direct conclusion.

## Finding-to-evidence ledger

Each material finding row must contain:

- stable `finding_id` and exact proposition (one falsifiable claim);
- chain ID and exact address(es);
- current pin or historical transaction/block/range;
- artifact basis and evidence type;
- classification: proven, strongly_supported, inference, or unknown;
- confidence and plausible alternatives;
- coverage/search universe, pagination/ranges, inclusion rule, and materiality threshold when it is a discovery claim;
- conditions that make the claim stale;
- report check/rating references.

An artifact citation is not enough: record exact method/parameters or transaction/log coordinates so another analyst can reproduce it. Clearly distinguish an absence found in a bounded search from a universal absence claim.

## Sellability table fields

For every tested size state input units/value, route and pool key/address, quote asset, pinned block, expected output, fee components, gas assumption, small-size unit output, holder-size unit output, degradation, price impact, slippage tolerance, result/failure reason, and evidence class. Mark quotes `read-only preview`; mark fork results `counterfactual`.

## Accounting presentation

Show each material asset separately:

`opening + inflows + explained adjustments = outflows + closing + bounded unexplained delta`

List transformations (wrap, swap, bridge, burn) without double-counting. Do not aggregate unlike assets using a spot price unless the conversion source/time is explicit and aggregation is useful to the user's question.

## Formal-report freeze

Before rendering, freeze the target manifest, report data, finding ledger, and hashes. Generate visuals only from that reconciled package. If formatting reveals an inconsistency, amend the evidence package and rerun validation; do not perform redundant research merely to populate design elements.

Passing `validate_case.py` proves internal identity, pin, hash, linkage, and declaration consistency only. It does **not** prove RPC honesty, source truth, discovery completeness, correct economic interpretation, or protocol safety.
