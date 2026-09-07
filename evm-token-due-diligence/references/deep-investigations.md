# Triggered deep investigations

Enter a track only when its trigger is met. State the trigger, evidence obtained, stop condition, and residual unknowns. A resource failure ends exact claims at the last supported bound; it does not create a pass or adverse token finding.

## Full holder or Transfer replay

- **Trigger:** concentration data conflicts; launch/current ownership is decision-critical; rebase/nonstandard accounting; material unexplained supply; snapshot API coverage is unclear.
- **Minimum evidence:** deployment/start block basis, complete declared log ranges and pagination, raw logs, token-specific mint/burn/rebase rules, balance checks at sampled/current pins, classified custody addresses, supply reconciliation.
- **Stop when:** reconstructed balances reconcile to pinned authoritative accounting within an explicitly justified bound and all material discrepancies are classified.
- **If incomplete:** report uncovered ranges/holders and that ranking or denominator may change; never label concentration acceptable.

## Complete pool and position history

- **Trigger:** “all liquidity locked” claim; multiple pools; transferred/modified positions; v4 hook/locker; material current depth or LP-fee-origin question.
- **Minimum evidence:** exact factories/managers searched, block ranges and event signatures, every material pool key/address, all position IDs/salts and custody transfers, liquidity modifications, fee collections, lockers/operators, current keyed state.
- **Stop when:** discovery universe and materiality threshold are declared, material positions reconcile from creation to current custody, and principal-versus-fee authority is resolved.
- **If incomplete:** identify missing manager/factory/range and leave side-pool/principal or fee-origin conclusions unknown.

## Launch-cohort accounting

- **Trigger:** sniper/insider concentration question; unusual early routing; fee exemptions/direct recipients; creator allocation; sales followed by rebuys.
- **Minimum evidence:** cohort definition before measurement, launch/deployment receipts and calldata, funding bounds, initial allocations, successful pool/curve executions, transfers, downstream inventory, proceeds, rebuys, fees, and retained assets.
- **Stop when:** each included wallet's inventory and proceeds reconcile within bounded unexplained delta, or additional hops are immaterial under the stated rule.
- **If incomplete:** state whether cohort membership, sale proof, funding, or destination coverage is missing. Describe sell/rebuy flows as market-mediated redistribution; zero balance is not cash-out.

## Fee-wallet and cross-chain proceeds reconciliation

- **Trigger:** treasury use, LP-fee provenance, creator proceeds, bridge movement, or profit/cash-out claim is decision-critical.
- **Minimum evidence:** per-asset opening/closing balances, successful receipts and decoded logs, claimed/collected versus unclaimed fees, wrap/swap/bridge transformations, gas, source/destination pins and matched bridge identifiers.
- **Stop when:** each asset equation closes within a disclosed bound, or commingling prevents further exact attribution.
- **If incomplete:** quantify the unexplained delta and stop at the last observable role. Do not claim sale, fiat withdrawal, beneficiary, or profit beyond it.

## Proxy authority and critical bytecode reconstruction

- **Trigger:** material contract lacks matched source; selector/storage behavior affects mint, seizure, restrictions, arbitrary call, upgrades, redemption, or LP removal; proxy path is unclear.
- **Minimum evidence:** runtime/hash, selector map, proxy/implementation/beacon/admin slots and calls, compiler metadata, verified predecessor/related runtimes where legitimate, historical successful calldata/receipts, key storage observations.
- **Escalation:** runtime and selectors → verified predecessors/compiler metadata → storage and historical calls → targeted decompilation/reconstruction → local-fork simulation only if needed.
- **Stop when:** the decision-relevant capability is directly demonstrated or ruled out within a defensible runtime/control boundary.
- **If incomplete:** name unresolved selectors/paths. Decompiler output remains an inference; executable equivalence requires reproducible compile and meaningful byte comparison.

## Reward-epoch accounting and backlog modeling

- **Trigger:** missed/duplicate payouts, claimed APR/entitlements, processing backlog, cumulative cap, vault solvency, or liveness is material.
- **Minimum evidence:** epoch/window definitions, eligible set and units, formula/config by epoch, funding/purchases/mints, cumulative claims, payment receipts, duplicate keys, retained inventory, processor calls/failures and capacity.
- **Stop when:** conservation and entitlement reconcile by epoch and backlog/capacity is bounded under stated assumptions.
- **If incomplete:** separate unpaid liability, unknown eligibility, unprocessed work, and insufficient backing. Do not assume distributions are bounded by same-period purchases.

## External dependency and redemption analysis

- **Trigger:** value/right depends on a wrapper, oracle, bridge, custodian, offchain API, keeper, lending venue, real-world asset, or discretionary redemption.
- **Minimum evidence:** dependency graph, exact contracts/operators, enforceable claimant and delivered asset, conversion units, caps/fees/timing, collateral/escrow, pause/upgrade/liquidation paths, current operational tests, and applicable authenticated terms if legal rights matter.
- **Stop when:** every step from holder claim to usable underlying asset is proven or a precise failure point makes the right conditional/unknown.
- **If incomplete:** call it inventory or a synthetic claim—not proven backing/redemption—and state the missing step.

## Narrow operational attribution

- **Trigger:** identifying an observed controller is necessary to assess authority, disclosure, sanctions/compliance, or a user-requested control claim.
- **Minimum evidence:** authenticated project-controlled sources, onchain role/signature evidence, multisig/governance membership where public and relevant, and exact temporal scope.
- **Stop when:** the operational role is established; do not expand into personal-identity research by default.
- **If incomplete:** retain neutral labels. Funding, routers, exchanges, timing, deterministic deployments, and settlement endpoints do not alone prove common ownership or human identity.
