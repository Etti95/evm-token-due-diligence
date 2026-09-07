# Portable case format

Use UTF-8 JSON/JSONL and relative paths. The validator has no third-party dependencies.

## Dependencies and portability

The packaged helpers require Python 3.10+ and use only the standard library. They make no network calls. A live investigation separately needs at least one JSON-RPC endpoint for each chain in scope and a way to preserve raw HTTP/JSON responses; public endpoints are acceptable if their archive/rate limits are recorded. ABI decoding, Keccak hashing, bytecode/source comparison, fork simulation, and report rendering may use locally available tools such as Foundry, a Solidity compiler, or equivalent open-source libraries, but none is assumed. Verify versions and chain deployments at run time, resolve the skill directory from the loaded `SKILL.md` location, and never hardcode personal paths, credentials, paid APIs, or another user's infrastructure.

## Directory layout

```text
case/
├── target-manifest.json
├── report.json
├── evidence-ledger.jsonl
└── evidence/
    ├── headers/<chain>-<block>.json
    └── ... raw RPC, receipts, calldata, code, decoded views
```

Run:

```bash
python3 /path/to/skill/scripts/validate_case.py /path/to/case
python3 /path/to/skill/scripts/artifact_digest.py /path/to/case/evidence/file.json
```

The validator deliberately rejects incomplete broad/formal packages. Focused answers can use the same format, but validation requires any checks/findings actually reported to be evidence-linked.

## `target-manifest.json`

Required top-level fields:

```json
{
  "schema_version": "1.0",
  "case_id": "stable-case-id",
  "mode": "broad",
  "decision_question": "Can privileged actors remove LP principal?",
  "requested_target": {"chain_id": 1, "address": "0x1111111111111111111111111111111111111111"},
  "observed_target": {"chain_id": 1, "address": "0x1111111111111111111111111111111111111111"},
  "metadata": {
    "name": {"status": "resolved", "value": "Example"},
    "symbol": {"status": "resolved", "value": "EX"},
    "decimals": {"status": "resolved", "value": 18},
    "total_supply": {"status": "resolved", "value": "1000000000000000000"}
  },
  "pins": [{
    "pin_id": "PIN-1",
    "chain_id": 1,
    "block_number": 19000000,
    "block_hash": "0x<64 hex>",
    "timestamp_utc": "2024-01-01T00:00:00Z",
    "captured_header": "evidence/headers/1-19000000.json",
    "header_sha256": "<64 hex>"
  }],
  "runtime": {
    "status": "resolved",
    "code_hash": "0x<64 hex>",
    "hash_algorithm": "keccak256",
    "proxy_kind": "none",
    "implementation": null,
    "beacon": null,
    "upgrade_authority": null,
    "source_correspondence": "runtime_matched"
  },
  "scope_addresses": [],
  "queries": [],
  "limitations": []
}
```

Metadata status is `resolved`, `nonstandard`, or `unresolved`. `value` must be present only for resolved/nonstandard states and null/absent for unresolved. Runtime status is `resolved`, `no_code`, or `unresolved`; unresolved requires a limitation. Source correspondence is `runtime_matched`, `proxy_only`, `candidate`, `unavailable`, `mismatch`, or `unresolved`.

Every material scope row requires `chain_id`, `address`, `role`, non-empty `provenance` evidence IDs, and `runtime_status` (`contract`, `eoa`, `native_or_precompile`, `destroyed_or_no_code`, `unresolved`). Contract rows require `runtime_hash`; unresolved rows require `limitation_id`.

Every query row requires:

```json
{
  "query_id": "Q-001",
  "evidence_id": "E-001",
  "target_binding": {"chain_id": 1, "address": "0x1111...1111"},
  "execution_chain_id": 1,
  "subject_address": "0x2222...2222",
  "block_number": 19000000,
  "method": "eth_getCode",
  "parameters": ["0x2222...2222", "0x121eac0"],
  "status": "success",
  "artifact": "evidence/q-001.json",
  "artifact_sha256": "<64 hex>"
}
```

Each query's target binding must equal the manifest target. Its execution chain must have its own pin. Include a successful, captured `eth_chainId` query for every chain; the validator parses its result and compares it with `execution_chain_id`. A successful query must reference a present, correctly hashed artifact. Error queries use status `error` and must reference a captured error artifact plus a `limitation_id`; they cannot support a passing check.

## Captured header

The header file may be the raw JSON-RPC result or an envelope with `result`. It must contain hex `number`, 32-byte `hash`, and hex `timestamp`. The validator converts the timestamp to UTC and compares all three values with the pin. A filename or manifest assertion is not proof of a pin.

## `report.json`

Required identity and declarations:

```json
{
  "schema_version": "1.0",
  "case_id": "stable-case-id",
  "mode": "broad",
  "target": {"chain_id": 1, "address": "0x1111...1111", "metadata": {}},
  "target_manifest": {"path": "target-manifest.json", "sha256": "<64 hex>"},
  "verdict": {"outcome": "CAUTION", "text": "Conditional conclusion", "time_basis": ["PIN-1"]},
  "declarations": {
    "no_real_private_keys_or_seed_phrases_requested_or_used": true,
    "no_real_transactions_signed": true,
    "no_transactions_broadcast": true,
    "simulations": []
  },
  "checks": [],
  "ratings": {},
  "findings": []
}
```

Target metadata must exactly mirror the manifest. Each check requires `check_id`, `result` (`pass`, `fail`, `mixed`, `unknown`, `not_applicable`), `evidence_state` (`proven`, `strongly_supported`, `inference`, `unknown`), `evidence_ids`, and `finding_ids`. `pass` is invalid with unknown/inference evidence, no evidence, an error-only query, or a linked unknown finding.

Broad/formal reports require all 11 rating keys listed in `reporting.md`. Each rating requires `severity`, `likelihood`, `confidence`, non-empty `coverage`, non-empty `time_basis`, `conclusion`, and `finding_ids`.

Every declared simulation requires `kind: local_disposable_fork`, `counterfactual: true`, fork chain/block matching a pin, `synthetic_accounts_only: true`, `broadcast_disabled: true`, and receipt plus intended balance-delta evidence IDs.

## `evidence-ledger.jsonl`

One JSON object per material finding:

```json
{"finding_id":"F-001","proposition":"Exact falsifiable claim","classification":"proven","confidence":"high","chain_id":1,"addresses":["0x1111...1111"],"time_basis":{"pin_chain_id":1,"pin_block_number":19000000},"evidence_ids":["E-001"],"artifacts":[{"evidence_id":"E-001","path":"evidence/q-001.json","sha256":"<64 hex>","type":"raw_rpc","locator":"eth_getCode params [...]"}],"alternatives":[],"coverage":"Exact included range/scope","stale_if":["implementation changes"]}
```

The report finding IDs/propositions/classifications must match the ledger. `unknown` findings may have no affirmative evidence but must state coverage/limitation. Proven and strongly supported findings need artifacts. Every artifact path is relative, inside the case directory, present, and hashed.

## What validation does not establish

A passing result validates internal consistency, not RPC honesty, source authenticity, discovery completeness, economic interpretation, exploit resistance, or protocol safety. Preserve independent evidence provenance and analyst judgment.
