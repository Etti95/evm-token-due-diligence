# EVM Token Due Diligence Skill

This repository contains `evm-token-due-diligence`, a reusable Codex agent skill for evidence-bounded diligence on an exact EVM token and its surrounding economic system.

It supports:

- focused questions, broad diligence, and formal reports;
- exact chain/address binding and block-pinned evidence;
- token privilege, proxy, liquidity-custody, sellability, concentration, launch, fee, treasury, reward, and redemption analysis;
- conditional procedures for Uniswap v3/v4, Pons-style launches, and Robinhood Chain;
- a target-integrity manifest, evidence ledger, case validator, and synthetic rejection tests.

The skill is not a price-prediction system, trading bot, generic scanner score, or substitute for a full protocol exploit audit.

## Install

Copy or link the skill directory into your Codex skills directory:

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R evm-token-due-diligence "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Restart Codex or begin a new session after installation.

## Validate the helpers

```sh
python3 -m unittest discover -s evm-token-due-diligence/tests -v
```

Validate a generated diligence case:

```sh
python3 evm-token-due-diligence/scripts/validate_case.py /path/to/case
```

Passing validation checks internal consistency: target identity, chain binding, captured block pins, artifact hashes, scope provenance, report/manifest agreement, and no-signing declarations. It does not establish RPC honesty, discovery completeness, economic correctness, or protocol safety.

## Usage examples

Focused:

```text
Use $evm-token-due-diligence in focused mode for chain ID 4663 and token
0x.... Determine who can remove canonical liquidity principal and whether
ordinary holders can sell 0.01%, 0.1%, and 1% of supply.
```

Broad:

```text
Use $evm-token-due-diligence in broad mode for chain ID 8453 and token
0x.... Screen all core risk surfaces and deepen only where evidence triggers it.
```

## Case-data policy

Per-address investigations, raw RPC evidence, bytecode captures, wallet mappings, and generated reports are intentionally excluded from version control. The reusable skill, references, validators, and synthetic tests are the only intended repository contents.

Never commit credentials, private keys, seed phrases, or real transaction-signing material.

