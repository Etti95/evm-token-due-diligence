# Evidence model and target packet

Use this reference for every case. The machine-checkable representation is in [case-format.md](case-format.md).

## Identity and pins

Normalize addresses only for comparison; preserve the observed representation in raw artifacts. Identity is `(chain_id, address)`, never name/symbol. Confirm each RPC with `eth_chainId`, and capture the full `eth_getBlockByNumber` response used for the current pin. Record:

- requested chain/address and RPC-observed chain/address;
- block number in integer form, 32-byte block hash, and UTC timestamp derived from the header timestamp;
- RPC method, parameters, response artifact, retrieval time, and redacted endpoint/provider description;
- a separate pin for every chain used, including bridge destinations.

Use the same pinned block tag for mutually compared current-state reads. If a provider cannot serve it, switch providers or mark the affected checks unknown; do not silently use `latest`. Historical transactions/logs are evidence at their own block and do not establish current state.

## Metadata and runtime

Call metadata on the target itself. Store name, symbol, decimals, and total supply as `resolved`, `nonstandard`, or `unresolved`; preserve raw returndata. A revert, malformed ABI response, bytes32 string, or missing method stays explicit. A matching symbol never repairs an identity mismatch.

Capture runtime bytecode at the pin and its Keccak-256 hash where tooling supports it; state the exact hash algorithm used. Detect common proxy patterns and inspect relevant storage slots/calls. Record implementation, beacon, admin, upgrade authority, and whether each was resolved at the same pin. Published source is:

- `runtime_matched` only after reproducible compilation/metadata handling and meaningful byte comparison;
- `proxy_only` if it covers the proxy but not implementation;
- `candidate` when discovered but not matched;
- `unavailable` or `mismatch` otherwise.

Do not call decompiler output verified source. Do not claim executable equivalence unless compilation and byte comparison close material differences.

## Architecture pass

Create a scope-address row for the token and every discovered pool, router, position manager, locker, hook, vault, escrow, treasury, distributor, oracle, bridge, proxy admin, multisig, timelock, or externally called contract that can affect the decision. Each material row needs:

- exact chain/address, neutral role, and discovery provenance;
- runtime status: contract, EOA, precompile/native sentinel, destroyed/no-code, or unresolved;
- runtime hash for contracts when available, or an explicit reason it is unavailable;
- relationship and authority paths;
- evidence IDs supporting classification.

Record keys and offchain actors separately when they have no contract address. “Owner is zero” or “renounced” applies only to the resolved control point, not the whole system.

## Raw evidence and query records

Preserve material JSON-RPC requests/responses, bytecode, calldata, receipts, and decoded logs. For every query record:

- freeze the canonical target binding;
- state execution chain, pinned block or historical transaction/block, subject address, RPC method/tool, full parameters, status, and artifact hash;
- redact credentials from filenames, parameters, bodies, and logs;
- record errors verbatim enough to distinguish timeout, pruning, rate limit, DNS, method absence, or malformed response.

Treat decoded material as a view over raw evidence; retain both. Verify event signature, emitting address, indexed fields, data types, successful receipt status, and log position before relying on a decoded log.

## Claim strength

- **Proven:** Direct, correctly interpreted primary evidence establishes the proposition within stated bounds.
- **Strongly supported:** Multiple coherent items support it, but a bounded gap prevents proof.
- **Inference:** Best explanation of evidence with plausible alternatives stated.
- **Unknown:** Missing, conflicting, inaccessible, or insufficient evidence.

Record alternatives and staleness conditions. A claim can be proven historically yet unknown currently. Tool failures affect coverage, not token risk. A skipped/unknown check cannot have a passing result.

## Simulations

Never request real credentials, impersonate a holder, sign a real transaction, or broadcast. Before any state-changing simulation verify and record:

1. local disposable fork process and upstream chain ID;
2. fork block matching the intended pin;
3. synthetic test accounts and synthetic funding/impersonation mechanism;
4. disabled or isolated broadcast path;
5. transaction request, trace/receipt, asset balance deltas, gas, route, and assumptions.

Label output `counterfactual local-fork simulation`. A successful simulated sale/redemption is decisive only for the tested state and inputs, and only when the intended underlying asset actually increases net of explained costs.

## Attribution boundary

Use observable roles until authenticated control evidence supports more. Shared funders, routers, exchange labels, timing, deterministic addresses, and common settlement destinations are signals, not identity proof. Call sale/rebuy patterns “market-mediated redistribution” absent stronger evidence. Stop exact proceeds attribution at commingling. An exchange deposit proves neither sale nor fiat withdrawal. Do not call proceeds profit without cost basis, material flows, fees, and retained inventory.
