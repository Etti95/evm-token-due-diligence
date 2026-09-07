# Core risk surfaces

Screen all sections in broad mode. In focused mode, use only the requested surface and dependencies required to make its answer sound.

## A. Token code and control

Inspect runtime and storage for mint, burn, rebase, balance rewrite, seizure, pause, blacklist/whitelist, taxes, exemptions, cooldown, wallet/transaction limits, trading gates, external calls, arbitrary call/delegatecall, and upgrade paths. Test both normal transfers and branches conditioned on sender, recipient, pool, router, block, amount, exemption, or trading state.

Resolve owners, roles, guardians, multisig signers/threshold, timelocks/delay/bypass paths, and who can change them. Separate:

- what current implementation executes;
- what current administrators can configure;
- what upgrade authority could introduce by replacement.

Trace role-admin relationships and pending ownership transfers. “Fixed supply” is about issuance, not seizure, taxes, sellability, LP custody, or an upgradeable surrounding system.

## B. Liquidity custody

Identify every material pool by exact address (v2/v3-style deployed pool) or complete pool key/PoolId (v4). Declare discovery sources, factories/managers, searched block ranges/pagination, inclusion thresholds, and gaps. Separate canonical from side pools and inactive/spoof pools.

Resolve the holder of each LP token or position, approvals/operators, position IDs, tick ranges, liquidity, unclaimed fees, lockers, hooks, and withdrawal authority. Inspect decrease/withdraw, collect, burn-position, rescue, arbitrary-call, approvals, transfer, upgrade, emergency, and migration paths. Determine who can remove **principal**, not merely collect fees.

A locked canonical position proves neither all-liquidity lock, price support, current in-range depth, nor side-pool safety. Report principal custody separately for canonical and side liquidity.

## C. Sellability and executable depth

When history is available, find a successful sell and verify receipt status, pool/curve state transition, token input, quote-asset output, sender/recipient routing, fees, and block. Router transfers alone do not prove a sale.

At the current pin obtain read-only quotes at:

- a small diagnostic size;
- user-requested or decision-relevant size;
- material holder-sized amounts tied to the concentration analysis.

Report input, route, pool/key, quote asset, expected output, fees, gas assumption if relevant, price impact, slippage tolerance separately, per-unit output, degradation versus the small quote, and exact failure reason. Quotes/previews do not prove realized exit; historical execution proves only that historical state.

If simulation is necessary, follow the fork restrictions in `evidence-model.md`. Require successful receipt plus intended underlying-asset balance delta.

## D. Supply and concentration

Reconcile total supply and material balances using the token's actual accounting. Separate raw assets, rebasing shares/units, synthetic claims, bond/NFT shares, LP positions, protocol custody, burn addresses, treasury, creator allocation, investor-like holdings, and circulating float.

State each concentration denominator and exclusions. Report at least material top-holder concentration and holder-sized exit implications; do not rank pools, lockers, or treasuries as ordinary investors. Use full Transfer replay only when triggered, and account for balance changes that do not emit ordinary Transfer events.

## E. Launch integrity

Resolve launch/deployment transaction and exact factory/version. Decode parameters, initial allocations, fee exemptions, buy recipients, funding, CREATE2 salts/addresses, sequence, and early transfers/sales. Distinguish automatic platform behavior from user-supplied exceptions.

Define wallet cohorts before measuring them: inclusion rule, time bounds, discovery sources, exclusions, and coverage. Track initial inventory, transfers, proven sales, rebuys, downstream inventory, proceeds, fees, and retained assets. A zero balance is not cash-out. A direct curve or pool buy may benefit a calldata-specified recipient rather than `tx.from`.

## F. Fees, treasury, and proceeds

Map the fee basis, asset denomination, fee bucket, splits, escrow, claim authority, configurable routes, recipients, and later use. Do not confuse percentage of gross trade value with percentage of the fee bucket. Separate present configuration from realized historical rates.

Reconcile each asset independently:

`opening balance + inflows + explained adjustments = outflows + closing balance + bounded unexplained delta`

Treat wrap/unwrap, burns, swaps, bridge legs, gas, internal transfers, and reverts correctly; do not double-count transformations. Stop exact attribution after commingling and state bounds.

## G. Rewards, vaults, backing, and redemption

Separate inventory, holder liabilities, promises, and enforceable rights. Determine eligible claimant, legal/onchain entitlement rule, actual asset delivered, units/conversion, fees, timing, caps, approval dependencies, admin controls, and exit path. A vault balance is not automatically backing; a synthetic claim is not automatically redeemable.

For “did these holdings come from LP fees?”, reconcile opening balance and every material receipt to position-level fee collection/forwarding receipts. Keep pool inventory, unclaimed fees, collected fees, and vault holdings distinct.

For distributions, test conservation, cumulative entitlements/caps, duplicate prevention, unpaid amounts, retained inventory, and processing liveness. Purchases need not cap distributions when prefunding, donations, carryover, or minting exist—prove the source.

## H. Utility, dependencies, and development

Test whether advertised utility is live, token-linked, and enforceable at the pin. Identify material external assets, oracles, bridges, sequencers, APIs, keepers, lending/collateral systems, custody, and redemption dependencies. Ask what failure, pause, depeg, censorship, admin action, or stale price changes the verdict.

Assess deployed-source correspondence, reproducible build evidence, tests, audit scope/version, release controls, governance, disclosures, and observed operation. Marketing polish, templates, or awkward code prove neither safety, fraud, nor AI authorship.

## Architecture-to-question closure

Before concluding, answer explicitly:

- What can privileged actors change or take?
- Who can remove canonical and side-pool principal?
- Can ordinary holders sell at realistic sizes under pinned state?
- How concentrated was launch and is ownership now?
- Where do fees and treasury assets go?
- What rights are executable by holders without discretionary cooperation?
- Which dependencies, custody arrangements, or unknowns could reverse the verdict?
