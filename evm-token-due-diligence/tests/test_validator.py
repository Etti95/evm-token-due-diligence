from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
from validate_case import RATING_KEYS, validate_case  # noqa: E402


TARGET = "0x1111111111111111111111111111111111111111"
WRONG_TARGET = "0x2222222222222222222222222222222222222222"
BLOCK_HASH = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
RUNTIME_HASH = "0x1234123412341234123412341234123412341234123412341234123412341234"
BLOCK_NUMBER = 19_000_000
TIMESTAMP = 1_700_000_000


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_case(root: Path) -> tuple[dict, dict]:
    evidence_dir = root / "evidence"
    header_path = evidence_dir / "headers" / "1-19000000.json"
    query_path = evidence_dir / "q-001.json"
    chain_query_path = evidence_dir / "q-chain.json"
    header = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "number": hex(BLOCK_NUMBER),
            "hash": BLOCK_HASH,
            "timestamp": hex(TIMESTAMP),
        },
    }
    query_artifact = {
        "request": {"method": "eth_getCode", "params": [TARGET, hex(BLOCK_NUMBER)]},
        "response": {"result": "0x60006000"},
    }
    chain_query_artifact = {
        "request": {"method": "eth_chainId", "params": []},
        "response": {"result": "0x1"},
    }
    write_json(header_path, header)
    write_json(query_path, query_artifact)
    write_json(chain_query_path, chain_query_artifact)
    metadata = {
        "name": {"status": "resolved", "value": "Synthetic Token"},
        "symbol": {"status": "resolved", "value": "SYN"},
        "decimals": {"status": "resolved", "value": 18},
        "total_supply": {"status": "resolved", "value": "1000000000000000000000"},
    }
    manifest = {
        "schema_version": "1.0",
        "case_id": "synthetic-valid-case",
        "mode": "broad",
        "decision_question": "Synthetic validation only; no live token finding.",
        "requested_target": {"chain_id": 1, "address": TARGET},
        "observed_target": {"chain_id": 1, "address": TARGET},
        "metadata": metadata,
        "pins": [
            {
                "pin_id": "PIN-1",
                "chain_id": 1,
                "block_number": BLOCK_NUMBER,
                "block_hash": BLOCK_HASH,
                "timestamp_utc": datetime.fromtimestamp(TIMESTAMP, timezone.utc).isoformat().replace("+00:00", "Z"),
                "captured_header": "evidence/headers/1-19000000.json",
                "header_sha256": sha(header_path),
            }
        ],
        "runtime": {
            "status": "resolved",
            "code_hash": RUNTIME_HASH,
            "hash_algorithm": "keccak256",
            "proxy_kind": "none",
            "implementation": None,
            "beacon": None,
            "upgrade_authority": None,
            "source_correspondence": "runtime_matched",
        },
        "scope_addresses": [
            {
                "chain_id": 1,
                "address": TARGET,
                "role": "target token",
                "provenance": ["E-001"],
                "runtime_status": "contract",
                "runtime_hash": RUNTIME_HASH,
            }
        ],
        "queries": [
            {
                "query_id": "Q-CHAIN",
                "evidence_id": "E-CHAIN",
                "target_binding": {"chain_id": 1, "address": TARGET},
                "execution_chain_id": 1,
                "subject_address": TARGET,
                "block_number": BLOCK_NUMBER,
                "method": "eth_chainId",
                "parameters": [],
                "status": "success",
                "artifact": "evidence/q-chain.json",
                "artifact_sha256": sha(chain_query_path),
            },
            {
                "query_id": "Q-001",
                "evidence_id": "E-001",
                "target_binding": {"chain_id": 1, "address": TARGET},
                "execution_chain_id": 1,
                "subject_address": TARGET,
                "block_number": BLOCK_NUMBER,
                "method": "eth_getCode",
                "parameters": [TARGET, hex(BLOCK_NUMBER)],
                "status": "success",
                "artifact": "evidence/q-001.json",
                "artifact_sha256": sha(query_path),
            }
        ],
        "limitations": [],
    }
    manifest_path = root / "target-manifest.json"
    write_json(manifest_path, manifest)
    ledger_row = {
        "finding_id": "F-001",
        "proposition": "The synthetic target had non-empty runtime in the captured synthetic response.",
        "classification": "proven",
        "confidence": "high",
        "chain_id": 1,
        "addresses": [TARGET],
        "time_basis": {"pin_chain_id": 1, "pin_block_number": BLOCK_NUMBER},
        "evidence_ids": ["E-001", "E-CHAIN"],
        "artifacts": [
            {
                "evidence_id": "E-001",
                "path": "evidence/q-001.json",
                "sha256": sha(query_path),
                "type": "raw_rpc",
                "locator": f"eth_getCode({TARGET}, {hex(BLOCK_NUMBER)})",
            },
            {
                "evidence_id": "E-CHAIN",
                "path": "evidence/q-chain.json",
                "sha256": sha(chain_query_path),
                "type": "raw_rpc",
                "locator": "eth_chainId()",
            },
        ],
        "alternatives": [],
        "coverage": "Only the synthetic eth_getCode response used by this validator test.",
        "stale_if": ["A different synthetic block is selected."],
    }
    (root / "evidence-ledger.jsonl").write_text(json.dumps(ledger_row, sort_keys=True) + "\n", encoding="utf-8")
    rating = {
        "severity": "informational",
        "likelihood": "unlikely",
        "confidence": "high",
        "coverage": "Synthetic validator fixture only.",
        "time_basis": ["PIN-1"],
        "conclusion": "No live diligence conclusion; validates package linkage only.",
        "finding_ids": ["F-001"],
    }
    report = {
        "schema_version": "1.0",
        "case_id": manifest["case_id"],
        "mode": "broad",
        "target": {"chain_id": 1, "address": TARGET, "metadata": metadata},
        "target_manifest": {"path": "target-manifest.json", "sha256": sha(manifest_path)},
        "verdict": {
            "outcome": "SYNTHETIC_ONLY",
            "text": "No live token finding; this package exists only to test validation behavior.",
            "time_basis": ["PIN-1"],
        },
        "declarations": {
            "no_real_private_keys_or_seed_phrases_requested_or_used": True,
            "no_real_transactions_signed": True,
            "no_transactions_broadcast": True,
            "simulations": [],
        },
        "checks": [
            {
                "check_id": "C-001",
                "result": "pass",
                "evidence_state": "proven",
                "evidence_ids": ["E-001"],
                "finding_ids": ["F-001"],
            }
        ],
        "ratings": {key: dict(rating) for key in RATING_KEYS},
        "findings": [
            {
                "finding_id": "F-001",
                "proposition": ledger_row["proposition"],
                "classification": "proven",
            }
        ],
    }
    write_json(root / "report.json", report)
    return manifest, report


def rewrite_manifest_and_report(root: Path, manifest: dict, report: dict) -> None:
    manifest_path = root / "target-manifest.json"
    write_json(manifest_path, manifest)
    report["target_manifest"]["sha256"] = sha(manifest_path)
    write_json(root / "report.json", report)


class ValidatorBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.manifest, self.report = make_case(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def assert_error_contains(self, needle: str) -> None:
        errors = validate_case(self.root)
        self.assertTrue(errors, "expected validation failure")
        self.assertTrue(any(needle in error for error in errors), f"missing {needle!r} in {errors!r}")

    def test_valid_synthetic_case_passes(self) -> None:
        self.assertEqual(validate_case(self.root), [])

    def test_rejects_same_symbol_token_substituted_from_another_chain(self) -> None:
        self.manifest["observed_target"]["chain_id"] = 10
        rewrite_manifest_and_report(self.root, self.manifest, self.report)
        self.assert_error_contains("same-symbol substitution rejected")

    def test_rejects_report_referring_to_wrong_target(self) -> None:
        self.report["target"]["address"] = WRONG_TARGET
        write_json(self.root / "report.json", self.report)
        self.assert_error_contains("report target address conflicts")

    def test_rejects_fake_or_inconsistent_block_pin(self) -> None:
        self.manifest["pins"][0]["block_hash"] = "0xabcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
        rewrite_manifest_and_report(self.root, self.manifest, self.report)
        self.assert_error_contains("block hash conflicts with captured header")

    def test_rejects_placeholder_block_pin(self) -> None:
        self.manifest["pins"][0]["block_hash"] = "0x" + "0" * 64
        rewrite_manifest_and_report(self.root, self.manifest, self.report)
        self.assert_error_contains("placeholder-looking hash")

    def test_rejects_unknown_check_presented_as_pass(self) -> None:
        self.report["checks"][0]["evidence_state"] = "unknown"
        write_json(self.root / "report.json", self.report)
        self.assert_error_contains("cannot be presented as pass")


if __name__ == "__main__":
    unittest.main()
