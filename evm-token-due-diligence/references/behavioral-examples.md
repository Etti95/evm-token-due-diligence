# Behavioral examples

These are synthetic reasoning patterns, not live findings.

## Locked canonical liquidity, removable side liquidity

Evidence proves the canonical v3 position NFT is held by a non-upgradeable locker with no current withdrawal path. A creator-controlled wallet owns a second material v3 position in another fee tier. Conclude: canonical LP-principal custody has no current executable removal path at the pin; side-pool removal risk is high for the second position. Do not summarize this as “liquidity locked.”

## Fixed supply, poor holder-sized exit

Runtime proves no mint path and supply reconciles. Pinned quotes return 9.9 WETH per unit at the small size, 5.4 at a top-holder-sized sale, and fail beyond that because initialized liquidity is exhausted. Conclude: token controls may be favorable on issuance, while holder-sized exit depth is severe. Fixed supply is not a sellability pass.

## Immutable token, upgradeable reward layer

The token runtime is non-proxy and has no owner. Rewards flow through a UUPS distributor whose admin can replace claim logic and rescue inventory. Conclude separately: token controls are immutable within examined runtime; reward custody/rights depend on upgrade authority. “Renounced token” does not make the economic system immutable.

## Launch wallets sell and rebuy for new recipients

Successful receipts show cohort wallets selling to the pool. Later buys funded from related proceeds deliver tokens to new calldata recipients. Record proven sales and recipient-specific buys, then describe the net pattern as market-mediated redistribution. Do not assume the new recipients are controlled by the sellers or call the difference profit without cost basis, fees, and retained inventory.

## Vault contains synthetic claims without proven exit

A vault holds claim tokens and distributes them, but no permissionless path from those claims to underlying assets is proven; redemption depends on an unresolved external custodian. Conclude that vault inventory exists, while underlying backing and enforceable exit remain unknown. Do not value the synthetic balance as liquid backing.

## RPC failure

Archive `eth_getLogs` times out for part of the launch range after bounded retries/providers. Record the missing range and provider error as a coverage limitation. Current state may still be proven at the pin, but launch concentration remains unknown. Never turn the timeout into either a launch-integrity pass or a token-risk finding.
