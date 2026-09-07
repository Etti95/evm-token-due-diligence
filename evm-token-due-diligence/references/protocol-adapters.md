# Protocol and chain adapters

Load only the applicable adapter. Contract deployments, chain metadata, factory versions, and interfaces change: verify them from official primary documentation and RPC for the case date. Never trust hardcoded addresses in this reference.

## Uniswap v3

Identify pools from the exact chain's canonical or explicitly named factory, then corroborate with factory events and `getPool(tokenA, tokenB, fee)`. For each material pool record token0/token1, fee, factory, pool address, creation block, slot0, current liquidity, initialized-tick coverage used for depth, and quote route.

Liquidity custody is position-specific. Resolve the exact NonfungiblePositionManager deployment and, for each token ID, owner, approvals, operator approvals, token pair, fee, tickLower/tickUpper, liquidity, owed fees, and current in-range status. Replay `IncreaseLiquidity`, `DecreaseLiquidity`, `Collect`, transfers, and burns when custody/history is material. Inspect any locker or custodian for unlock time, beneficiary, emergency/rescue paths, arbitrary calls, approvals, upgradeability, and admin keys.

Do not infer reserves or executable depth from pool token balances alone. Do not call fee collection principal removal: distinguish `collect` of owed fees from liquidity decrease and position transfer.

## Uniswap v4

V4 is singleton-based: a pool is not identified by a unique pool contract. Record the exact PoolManager deployment and complete `PoolKey`:

- sorted `currency0` and `currency1` (native currency may use the zero-address sentinel);
- LP fee including dynamic-fee flag/meaning;
- signed tick spacing;
- hooks address;
- derived `PoolId` and the exact derivation/encoding implementation used.

Confirm the key from initialization events and pinned state. The PoolManager's aggregate token balance is **not** a pool's reserves. Read pool-keyed state and reconstruct initialized ticks/liquidity as needed for depth. Account for flash accounting and settlement deltas in transaction analysis.

Resolve the exact PositionManager or protocol-specific position/locker representation, position identifiers/salts, owner or claimant, approvals/operators, liquidity ranges, and removal path. V4 hooks are part of pool behavior: decode hook-permission address bits where applicable and inspect implemented callbacks, dynamic fees, before/after swap deltas, withdrawal/fee paths, external calls, upgrade/control, and dependencies. Treat the hook as an independent risk surface, not as Uniswap core.

Official Uniswap documentation describes the singleton PoolManager and complete PoolKey model; verify the deployed version and chain address at investigation time:

- https://developers.uniswap.org/docs/protocols/v4/concepts/poolmanager
- https://developers.uniswap.org/docs/protocols/v4/guides/read-pool-state
- https://developers.uniswap.org/docs/protocols/v4/guides/create-pool

## Pons-family launches

“Pons” may refer to different deployed generations or related launch systems with materially different mechanics. Do not apply one version's documentation to another. From the exact launch transaction and factory runtime:

1. identify chain, factory, implementation/version, deployer, curve/pool, token, locker, hook, escrow, vault, routers, and any graduation executor;
2. decode user-controlled fields such as creator/fee wallet, initial buy amount, buy recipient, exemptions, quote token, selected community/token, salt, hook data, and slippage bounds;
3. verify supply destination and whether trading begins on a curve, a v4 pool, or another mechanism;
4. identify protection windows/limits and their exact recipients/exemptions from deployed code;
5. determine pre/post-graduation sale paths, graduation conditions, atomicity, pool key, position custody, fee routing, buyback/vesting, safety/recovery, migration, and admin paths;
6. reconcile direct buy consideration with the calldata recipient and applied tax/fee branch. Never assume `tx.from` received the tokens or economic benefit.

Treat platform claims such as fixed supply, permanent lock, permissionless graduation, or no migration as hypotheses until matched to the exact deployed version. Current public documentation itself shows why version resolution matters: Pons documentation describes both direct-pool launches and a v2 curve-to-v4 graduation architecture. Use it only for discovery and then verify runtime/receipts:

- https://docs.ponsfamily.com/
- https://docs.ponsfamily.com/v2

## Robinhood Chain

Verify `eth_chainId` from the endpoint and verify current network parameters from official Robinhood Chain documentation; do not infer mainnet/testnet from hostname or wallet label. Capture the chain's own pin. As of the skill's packaging, official documentation lists distinct Robinhood Chain mainnet and testnet IDs, but these values are discovery hints, not substitutes for RPC verification:

- https://docs.robinhood.com/chain/connecting/
- https://robinhood.com/us/en/support/articles/robinhood-chain-testnet/

Treat it as an EVM L2 with additional dependency questions. Identify the rollup deployment/version, settlement chain, data availability mode, sequencer behavior, finality/confirmation assumptions, canonical bridge/inbox/outbox contracts, upgrade/security council powers, pause/censorship/forced-inclusion path, native gas asset, and explorer/RPC archive coverage. Verify contract addresses from official chain configuration plus runtime.

For bridged or tokenized assets, distinguish native issuance, canonical bridge representation, third-party bridge wrapper, custodian-issued claim, and synthetic asset. Map mint/burn authority, escrow on the origin chain, bridge upgrade/pause, withdrawal delay, final recipient, redemption eligibility, transfer restrictions, oracle/trading-hours dependencies, and legal/custodial terms when they determine enforceable rights. Never equate a ticker resembling an equity or asset with a direct claim on that asset.

## Cross-chain tracing

Pin both chains. Match source receipt, bridge contract and method/event, message or transfer identifier, source asset/amount/sender/destination recipient, destination execution, delivered asset/amount, and destination evidence. Explain fees, decimal conversion, wrappers, partial delivery, and finality. A source deposit alone does not prove destination delivery. Stop attribution when funds commingle or leave observable scope.
