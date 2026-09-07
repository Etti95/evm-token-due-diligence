#!/usr/bin/env python3
"""Validate the internal consistency of an EVM diligence case package.

This deliberately does not contact an RPC or judge protocol safety. It validates
identity binding, captured pins, artifact hashes, evidence linkage, report-source
identity, and simulation/signing declarations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
HASH_RE = re.compile(r"^0x[0-9a-fA-F]{64}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

METADATA_FIELDS = ("name", "symbol", "decimals", "total_supply")
METADATA_STATES = {"resolved", "nonstandard", "unresolved"}
CLASSIFICATIONS = {"proven", "strongly_supported", "inference", "unknown"}
RATING_KEYS = (
    "token_controls",
    "canonical_lp_principal_custody",
    "side_pool_removal_risk",
    "sellability_and_exit_depth",
    "current_concentration",
    "historical_launch_integrity",
    "admin_treasury_and_reward_custody",
    "reward_accounting_and_liveness",
    "utility_and_redemption_rights",
    "external_dependencies",
    "development_and_disclosure",
)


class Collector:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path, collector: Collector, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        collector.errors.append(f"{label}: missing file {path}")
        return {}
    except (OSError, json.JSONDecodeError) as exc:
        collector.errors.append(f"{label}: cannot read valid JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        collector.errors.append(f"{label}: top level must be an object")
        return {}
    return value


def load_jsonl(path: Path, collector: Collector) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        collector.errors.append(f"ledger: missing file {path}")
        return rows
    except OSError as exc:
        collector.errors.append(f"ledger: cannot read: {exc}")
        return rows
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            collector.errors.append(f"ledger line {number}: invalid JSON: {exc}")
            continue
        if not isinstance(row, dict):
            collector.errors.append(f"ledger line {number}: must be an object")
            continue
        rows.append(row)
    return rows


def safe_case_path(case_dir: Path, relative: Any, collector: Collector, label: str) -> Path | None:
    if not isinstance(relative, str) or not relative.strip():
        collector.errors.append(f"{label}: path must be a non-empty relative string")
        return None
    candidate = (case_dir / relative).resolve()
    try:
        candidate.relative_to(case_dir)
    except ValueError:
        collector.errors.append(f"{label}: path escapes case directory: {relative}")
        return None
    return candidate


def normalized_address(value: Any, collector: Collector, label: str, allow_zero: bool = False) -> str | None:
    if not isinstance(value, str) or not ADDRESS_RE.fullmatch(value):
        collector.errors.append(f"{label}: malformed EVM address")
        return None
    result = value.lower()
    if not allow_zero and result == "0x" + "0" * 40:
        collector.errors.append(f"{label}: zero/placeholder address is not allowed")
        return None
    return result


def valid_hash(value: Any, collector: Collector, label: str, reject_placeholder: bool = True) -> bool:
    if not isinstance(value, str) or not HASH_RE.fullmatch(value):
        collector.errors.append(f"{label}: expected 0x-prefixed 32-byte hash")
        return False
    body = value[2:].lower()
    if reject_placeholder and (len(set(body)) <= 2 or body in {"0" * 64, "f" * 64}):
        collector.errors.append(f"{label}: placeholder-looking hash is rejected")
        return False
    return True


def parse_int(value: Any, collector: Collector, label: str) -> int | None:
    if isinstance(value, bool):
        collector.errors.append(f"{label}: expected integer")
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value, 16) if value.startswith("0x") else int(value)
        except ValueError:
            pass
    collector.errors.append(f"{label}: expected integer or hex quantity")
    return None


def utc_from_unix(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat().replace("+00:00", "Z")


def check_artifact(
    case_dir: Path,
    relative: Any,
    expected: Any,
    collector: Collector,
    label: str,
) -> Path | None:
    path = safe_case_path(case_dir, relative, collector, label)
    if path is None:
        return None
    if not path.is_file():
        collector.errors.append(f"{label}: missing artifact {relative}")
        return None
    if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
        collector.errors.append(f"{label}: malformed SHA-256 digest")
        return path
    actual = sha256_file(path)
    if actual != expected:
        collector.errors.append(f"{label}: SHA-256 mismatch (expected {expected}, got {actual})")
    return path


def validate_metadata(manifest: dict[str, Any], collector: Collector) -> dict[str, Any]:
    metadata = manifest.get("metadata")
    collector.require(isinstance(metadata, dict), "manifest.metadata: required object")
    if not isinstance(metadata, dict):
        return {}
    for field in METADATA_FIELDS:
        item = metadata.get(field)
        collector.require(isinstance(item, dict), f"manifest.metadata.{field}: required object")
        if not isinstance(item, dict):
            continue
        state = item.get("status")
        collector.require(state in METADATA_STATES, f"manifest.metadata.{field}: invalid status")
        if state == "unresolved":
            collector.require(item.get("value") is None, f"manifest.metadata.{field}: unresolved must not have a value")
            collector.require(bool(item.get("reason")), f"manifest.metadata.{field}: unresolved requires reason")
        else:
            collector.require("value" in item and item.get("value") is not None, f"manifest.metadata.{field}: {state} requires value")
    return metadata


def validate_pins(case_dir: Path, manifest: dict[str, Any], collector: Collector) -> tuple[dict[int, dict[str, Any]], set[str]]:
    pins = manifest.get("pins")
    collector.require(isinstance(pins, list) and bool(pins), "manifest.pins: at least one pin is required")
    if not isinstance(pins, list):
        return {}, set()
    by_chain: dict[int, dict[str, Any]] = {}
    pin_ids: set[str] = set()
    for index, pin in enumerate(pins):
        label = f"manifest.pins[{index}]"
        if not isinstance(pin, dict):
            collector.errors.append(f"{label}: must be an object")
            continue
        pin_id = pin.get("pin_id")
        collector.require(isinstance(pin_id, str) and bool(pin_id.strip()), f"{label}.pin_id: required")
        if isinstance(pin_id, str):
            collector.require(pin_id not in pin_ids, f"{label}.pin_id: duplicate {pin_id}")
            pin_ids.add(pin_id)
        chain_id = parse_int(pin.get("chain_id"), collector, f"{label}.chain_id")
        block_number = parse_int(pin.get("block_number"), collector, f"{label}.block_number")
        valid_hash(pin.get("block_hash"), collector, f"{label}.block_hash")
        collector.require(chain_id is not None and chain_id > 0, f"{label}.chain_id: must be positive")
        collector.require(block_number is not None and block_number > 0, f"{label}.block_number: placeholder/non-positive pin rejected")
        if chain_id is not None:
            collector.require(chain_id not in by_chain, f"{label}: duplicate pin for chain {chain_id}")
            by_chain[chain_id] = pin
        header_path = check_artifact(
            case_dir, pin.get("captured_header"), pin.get("header_sha256"), collector, f"{label}.captured_header"
        )
        if header_path is None:
            continue
        header = load_json(header_path, collector, f"{label}.header")
        if isinstance(header.get("result"), dict):
            header = header["result"]
        header_number = parse_int(header.get("number"), collector, f"{label}.header.number")
        header_timestamp = parse_int(header.get("timestamp"), collector, f"{label}.header.timestamp")
        header_hash = header.get("hash")
        valid_hash(header_hash, collector, f"{label}.header.hash")
        collector.require(header_number == block_number, f"{label}: block number conflicts with captured header")
        if isinstance(header_hash, str) and isinstance(pin.get("block_hash"), str):
            collector.require(header_hash.lower() == pin["block_hash"].lower(), f"{label}: block hash conflicts with captured header")
        if header_timestamp is not None:
            try:
                expected_utc = utc_from_unix(header_timestamp)
            except (OverflowError, OSError, ValueError):
                collector.errors.append(f"{label}.header.timestamp: out of range")
            else:
                collector.require(pin.get("timestamp_utc") == expected_utc, f"{label}: UTC timestamp conflicts with captured header ({expected_utc})")
    return by_chain, pin_ids


def validate_runtime(manifest: dict[str, Any], limitation_ids: set[str], collector: Collector) -> None:
    runtime = manifest.get("runtime")
    collector.require(isinstance(runtime, dict), "manifest.runtime: required object")
    if not isinstance(runtime, dict):
        return
    status = runtime.get("status")
    collector.require(status in {"resolved", "no_code", "unresolved"}, "manifest.runtime.status: invalid")
    if status == "resolved":
        valid_hash(runtime.get("code_hash"), collector, "manifest.runtime.code_hash", reject_placeholder=False)
        collector.require(bool(runtime.get("hash_algorithm")), "manifest.runtime.hash_algorithm: required")
    if status == "unresolved":
        collector.require(runtime.get("limitation_id") in limitation_ids, "manifest.runtime: unresolved requires valid limitation_id")
    collector.require(
        runtime.get("source_correspondence") in {"runtime_matched", "proxy_only", "candidate", "unavailable", "mismatch", "unresolved"},
        "manifest.runtime.source_correspondence: invalid",
    )
    collector.require("proxy_kind" in runtime, "manifest.runtime.proxy_kind: required")
    for field in ("implementation", "beacon", "upgrade_authority"):
        value = runtime.get(field)
        if value is not None:
            normalized_address(value, collector, f"manifest.runtime.{field}")


def validate_case(case_dir: Path) -> list[str]:
    collector = Collector()
    case_dir = case_dir.resolve()
    manifest_path = case_dir / "target-manifest.json"
    report_path = case_dir / "report.json"
    ledger_path = case_dir / "evidence-ledger.jsonl"
    manifest = load_json(manifest_path, collector, "manifest")
    report = load_json(report_path, collector, "report")
    ledger = load_jsonl(ledger_path, collector)

    collector.require(manifest.get("schema_version") == "1.0", "manifest.schema_version: expected 1.0")
    collector.require(report.get("schema_version") == "1.0", "report.schema_version: expected 1.0")
    case_id = manifest.get("case_id")
    collector.require(isinstance(case_id, str) and bool(case_id.strip()), "manifest.case_id: required")
    collector.require(report.get("case_id") == case_id, "report.case_id conflicts with manifest")
    mode = manifest.get("mode")
    collector.require(mode in {"focused", "broad", "formal"}, "manifest.mode: invalid")
    collector.require(report.get("mode") == mode, "report.mode conflicts with manifest")
    collector.require(bool(manifest.get("decision_question")), "manifest.decision_question: required")

    requested = manifest.get("requested_target") if isinstance(manifest.get("requested_target"), dict) else {}
    observed = manifest.get("observed_target") if isinstance(manifest.get("observed_target"), dict) else {}
    report_target = report.get("target") if isinstance(report.get("target"), dict) else {}
    req_chain = parse_int(requested.get("chain_id"), collector, "manifest.requested_target.chain_id")
    obs_chain = parse_int(observed.get("chain_id"), collector, "manifest.observed_target.chain_id")
    rep_chain = parse_int(report_target.get("chain_id"), collector, "report.target.chain_id")
    req_address = normalized_address(requested.get("address"), collector, "manifest.requested_target.address")
    obs_address = normalized_address(observed.get("address"), collector, "manifest.observed_target.address")
    rep_address = normalized_address(report_target.get("address"), collector, "report.target.address")
    collector.require(req_chain is not None and req_chain > 0, "manifest.requested_target.chain_id: must be positive")
    collector.require(req_chain == obs_chain, "requested and RPC-observed chain IDs conflict (same-symbol substitution rejected)")
    collector.require(req_address == obs_address, "requested and RPC-observed target addresses conflict")
    collector.require(req_chain == rep_chain, "report target chain conflicts with manifest")
    collector.require(req_address == rep_address, "report target address conflicts with manifest")

    metadata = validate_metadata(manifest, collector)
    collector.require(report_target.get("metadata") == metadata, "report target metadata must exactly mirror manifest metadata")

    limitations = manifest.get("limitations")
    collector.require(isinstance(limitations, list), "manifest.limitations: required list")
    limitation_ids: set[str] = set()
    if isinstance(limitations, list):
        for index, limitation in enumerate(limitations):
            label = f"manifest.limitations[{index}]"
            collector.require(isinstance(limitation, dict), f"{label}: must be object")
            if not isinstance(limitation, dict):
                continue
            limitation_id = limitation.get("limitation_id")
            collector.require(isinstance(limitation_id, str) and bool(limitation_id), f"{label}.limitation_id: required")
            if isinstance(limitation_id, str):
                collector.require(limitation_id not in limitation_ids, f"{label}: duplicate limitation_id")
                limitation_ids.add(limitation_id)
            collector.require(bool(limitation.get("description")), f"{label}.description: required")

    pins_by_chain, pin_ids = validate_pins(case_dir, manifest, collector)
    if req_chain is not None:
        collector.require(req_chain in pins_by_chain, "primary target chain has no captured pin")
    validate_runtime(manifest, limitation_ids, collector)

    # Validate ledger and collect evidence IDs before checking scope/query/report links.
    ledger_by_finding: dict[str, dict[str, Any]] = {}
    evidence_registry: dict[str, tuple[Any, Any, Any, Any]] = {}
    evidence_ids: set[str] = set()
    evidence_from_error_queries: set[str] = set()
    for index, row in enumerate(ledger):
        label = f"ledger[{index}]"
        finding_id = row.get("finding_id")
        collector.require(isinstance(finding_id, str) and bool(finding_id), f"{label}.finding_id: required")
        if not isinstance(finding_id, str):
            continue
        collector.require(finding_id not in ledger_by_finding, f"{label}: duplicate finding_id {finding_id}")
        ledger_by_finding[finding_id] = row
        collector.require(bool(row.get("proposition")), f"{label}.proposition: required")
        classification = row.get("classification")
        collector.require(classification in CLASSIFICATIONS, f"{label}.classification: invalid")
        collector.require(row.get("confidence") in {"high", "medium", "low", "unknown"}, f"{label}.confidence: invalid")
        chain_id = parse_int(row.get("chain_id"), collector, f"{label}.chain_id")
        collector.require(chain_id in pins_by_chain, f"{label}: chain has no captured pin")
        addresses = row.get("addresses")
        collector.require(isinstance(addresses, list) and bool(addresses), f"{label}.addresses: non-empty list required")
        if isinstance(addresses, list):
            for address_index, address in enumerate(addresses):
                normalized_address(address, collector, f"{label}.addresses[{address_index}]", allow_zero=True)
        collector.require(bool(row.get("coverage")), f"{label}.coverage: required")
        collector.require(isinstance(row.get("alternatives"), list), f"{label}.alternatives: list required")
        collector.require(isinstance(row.get("stale_if"), list) and bool(row.get("stale_if")), f"{label}.stale_if: non-empty list required")
        time_basis = row.get("time_basis")
        collector.require(isinstance(time_basis, dict) and bool(time_basis), f"{label}.time_basis: required")
        artifacts = row.get("artifacts")
        collector.require(isinstance(artifacts, list), f"{label}.artifacts: list required")
        if classification in {"proven", "strongly_supported"}:
            collector.require(isinstance(artifacts, list) and bool(artifacts), f"{label}: {classification} requires artifacts")
        artifact_eids: set[str] = set()
        if isinstance(artifacts, list):
            for artifact_index, artifact in enumerate(artifacts):
                artifact_label = f"{label}.artifacts[{artifact_index}]"
                collector.require(isinstance(artifact, dict), f"{artifact_label}: must be object")
                if not isinstance(artifact, dict):
                    continue
                evidence_id = artifact.get("evidence_id")
                collector.require(isinstance(evidence_id, str) and bool(evidence_id), f"{artifact_label}.evidence_id: required")
                if isinstance(evidence_id, str):
                    signature = (artifact.get("path"), artifact.get("sha256"), artifact.get("type"), artifact.get("locator"))
                    if evidence_id in evidence_registry:
                        collector.require(evidence_registry[evidence_id] == signature, f"{artifact_label}: evidence ID {evidence_id} conflicts with its earlier artifact identity")
                    else:
                        evidence_registry[evidence_id] = signature
                    evidence_ids.add(evidence_id)
                    artifact_eids.add(evidence_id)
                collector.require(bool(artifact.get("type")), f"{artifact_label}.type: required")
                collector.require(bool(artifact.get("locator")), f"{artifact_label}.locator: reproducible locator required")
                check_artifact(case_dir, artifact.get("path"), artifact.get("sha256"), collector, artifact_label)
        declared_eids = row.get("evidence_ids")
        collector.require(isinstance(declared_eids, list), f"{label}.evidence_ids: list required")
        if isinstance(declared_eids, list):
            collector.require(set(declared_eids) == artifact_eids, f"{label}.evidence_ids must exactly match artifact evidence IDs")

    scope = manifest.get("scope_addresses")
    collector.require(isinstance(scope, list) and bool(scope), "manifest.scope_addresses: non-empty list required")
    target_scope_found = False
    seen_scope: set[tuple[int, str]] = set()
    if isinstance(scope, list):
        for index, item in enumerate(scope):
            label = f"manifest.scope_addresses[{index}]"
            collector.require(isinstance(item, dict), f"{label}: must be object")
            if not isinstance(item, dict):
                continue
            chain_id = parse_int(item.get("chain_id"), collector, f"{label}.chain_id")
            address = normalized_address(item.get("address"), collector, f"{label}.address", allow_zero=item.get("runtime_status") == "native_or_precompile")
            collector.require(chain_id in pins_by_chain, f"{label}: chain has no captured pin")
            if chain_id is not None and address is not None:
                key = (chain_id, address)
                collector.require(key not in seen_scope, f"{label}: duplicate scope identity")
                seen_scope.add(key)
                if chain_id == req_chain and address == req_address:
                    target_scope_found = True
            collector.require(bool(item.get("role")), f"{label}.role: required")
            provenance = item.get("provenance")
            collector.require(isinstance(provenance, list) and bool(provenance), f"{label}.provenance: non-empty evidence ID list required")
            if isinstance(provenance, list):
                for evidence_id in provenance:
                    collector.require(evidence_id in evidence_ids, f"{label}.provenance: unknown evidence ID {evidence_id}")
            status = item.get("runtime_status")
            collector.require(status in {"contract", "eoa", "native_or_precompile", "destroyed_or_no_code", "unresolved"}, f"{label}.runtime_status: invalid")
            if status == "contract":
                valid_hash(item.get("runtime_hash"), collector, f"{label}.runtime_hash", reject_placeholder=False)
            if status == "unresolved":
                collector.require(item.get("limitation_id") in limitation_ids, f"{label}: unresolved requires valid limitation_id")
    collector.require(target_scope_found, "manifest.scope_addresses must include the exact target token")

    queries = manifest.get("queries")
    collector.require(isinstance(queries, list), "manifest.queries: required list")
    rpc_verified_chains: set[int] = set()
    if isinstance(queries, list):
        seen_queries: set[str] = set()
        for index, query in enumerate(queries):
            label = f"manifest.queries[{index}]"
            collector.require(isinstance(query, dict), f"{label}: must be object")
            if not isinstance(query, dict):
                continue
            query_id = query.get("query_id")
            collector.require(isinstance(query_id, str) and bool(query_id), f"{label}.query_id: required")
            if isinstance(query_id, str):
                collector.require(query_id not in seen_queries, f"{label}: duplicate query_id")
                seen_queries.add(query_id)
            binding = query.get("target_binding") if isinstance(query.get("target_binding"), dict) else {}
            bind_chain = parse_int(binding.get("chain_id"), collector, f"{label}.target_binding.chain_id")
            bind_address = normalized_address(binding.get("address"), collector, f"{label}.target_binding.address")
            collector.require(bind_chain == req_chain and bind_address == req_address, f"{label}: target binding conflicts with exact requested target")
            execution_chain = parse_int(query.get("execution_chain_id"), collector, f"{label}.execution_chain_id")
            collector.require(execution_chain in pins_by_chain, f"{label}: execution chain has no captured pin")
            normalized_address(query.get("subject_address"), collector, f"{label}.subject_address", allow_zero=True)
            collector.require(bool(query.get("method")), f"{label}.method: required")
            collector.require("parameters" in query, f"{label}.parameters: required")
            status = query.get("status")
            collector.require(status in {"success", "error"}, f"{label}.status: invalid")
            query_artifact_path = check_artifact(case_dir, query.get("artifact"), query.get("artifact_sha256"), collector, label)
            if status == "error":
                collector.require(query.get("limitation_id") in limitation_ids, f"{label}: error requires valid limitation_id")
            if query.get("method") == "eth_chainId" and status == "success" and query_artifact_path is not None:
                chain_payload = load_json(query_artifact_path, collector, f"{label}.chain_id_artifact")
                if isinstance(chain_payload.get("response"), dict):
                    chain_payload = chain_payload["response"]
                rpc_chain_id = parse_int(chain_payload.get("result"), collector, f"{label}.chain_id_artifact.result")
                collector.require(rpc_chain_id == execution_chain, f"{label}: eth_chainId response conflicts with execution_chain_id")
                if rpc_chain_id == execution_chain and execution_chain is not None:
                    rpc_verified_chains.add(execution_chain)
            evidence_id = query.get("evidence_id")
            if evidence_id is not None:
                collector.require(evidence_id in evidence_ids, f"{label}.evidence_id: not found in ledger artifacts")
                if isinstance(evidence_id, str):
                    if status == "error":
                        evidence_from_error_queries.add(evidence_id)
    for chain_id in pins_by_chain:
        collector.require(chain_id in rpc_verified_chains, f"manifest.queries: chain {chain_id} lacks a successful captured eth_chainId verification")

    source = report.get("target_manifest") if isinstance(report.get("target_manifest"), dict) else {}
    source_path = safe_case_path(case_dir, source.get("path"), collector, "report.target_manifest.path")
    if source_path is not None:
        collector.require(source_path == manifest_path.resolve(), "report.target_manifest.path must identify this case's target-manifest.json")
    check_artifact(case_dir, source.get("path"), source.get("sha256"), collector, "report.target_manifest")

    declarations = report.get("declarations")
    collector.require(isinstance(declarations, dict), "report.declarations: required object")
    simulations: list[Any] = []
    if isinstance(declarations, dict):
        for key in (
            "no_real_private_keys_or_seed_phrases_requested_or_used",
            "no_real_transactions_signed",
            "no_transactions_broadcast",
        ):
            collector.require(declarations.get(key) is True, f"report.declarations.{key}: must be true")
        simulations = declarations.get("simulations")
        collector.require(isinstance(simulations, list), "report.declarations.simulations: required list")
    if isinstance(simulations, list):
        for index, simulation in enumerate(simulations):
            label = f"report.declarations.simulations[{index}]"
            collector.require(isinstance(simulation, dict), f"{label}: must be object")
            if not isinstance(simulation, dict):
                continue
            collector.require(simulation.get("kind") == "local_disposable_fork", f"{label}.kind: must be local_disposable_fork")
            collector.require(simulation.get("counterfactual") is True, f"{label}.counterfactual: must be true")
            collector.require(simulation.get("synthetic_accounts_only") is True, f"{label}.synthetic_accounts_only: must be true")
            collector.require(simulation.get("broadcast_disabled") is True, f"{label}.broadcast_disabled: must be true")
            fork_chain = parse_int(simulation.get("fork_chain_id"), collector, f"{label}.fork_chain_id")
            fork_block = parse_int(simulation.get("fork_block_number"), collector, f"{label}.fork_block_number")
            collector.require(fork_chain in pins_by_chain, f"{label}: fork chain has no pin")
            if fork_chain in pins_by_chain:
                collector.require(fork_block == pins_by_chain[fork_chain].get("block_number"), f"{label}: fork block does not match captured pin")
            for key in ("receipt_evidence_id", "intended_balance_delta_evidence_id"):
                collector.require(simulation.get(key) in evidence_ids, f"{label}.{key}: valid evidence ID required")

    report_findings = report.get("findings")
    collector.require(isinstance(report_findings, list), "report.findings: required list")
    report_finding_ids: set[str] = set()
    if isinstance(report_findings, list):
        for index, finding in enumerate(report_findings):
            label = f"report.findings[{index}]"
            collector.require(isinstance(finding, dict), f"{label}: must be object")
            if not isinstance(finding, dict):
                continue
            finding_id = finding.get("finding_id")
            collector.require(finding_id in ledger_by_finding, f"{label}: finding_id missing from ledger")
            if isinstance(finding_id, str):
                report_finding_ids.add(finding_id)
                ledger_row = ledger_by_finding.get(finding_id, {})
                collector.require(finding.get("proposition") == ledger_row.get("proposition"), f"{label}: proposition conflicts with ledger")
                collector.require(finding.get("classification") == ledger_row.get("classification"), f"{label}: classification conflicts with ledger")
    collector.require(report_finding_ids == set(ledger_by_finding), "report and ledger finding sets must match exactly")

    checks = report.get("checks")
    collector.require(isinstance(checks, list), "report.checks: required list")
    if isinstance(checks, list):
        seen_checks: set[str] = set()
        for index, check in enumerate(checks):
            label = f"report.checks[{index}]"
            collector.require(isinstance(check, dict), f"{label}: must be object")
            if not isinstance(check, dict):
                continue
            check_id = check.get("check_id")
            collector.require(isinstance(check_id, str) and bool(check_id), f"{label}.check_id: required")
            if isinstance(check_id, str):
                collector.require(check_id not in seen_checks, f"{label}: duplicate check_id")
                seen_checks.add(check_id)
            result = check.get("result")
            evidence_state = check.get("evidence_state")
            collector.require(result in {"pass", "fail", "mixed", "unknown", "not_applicable"}, f"{label}.result: invalid")
            collector.require(evidence_state in CLASSIFICATIONS, f"{label}.evidence_state: invalid")
            linked_evidence = check.get("evidence_ids")
            linked_findings = check.get("finding_ids")
            collector.require(isinstance(linked_evidence, list), f"{label}.evidence_ids: list required")
            collector.require(isinstance(linked_findings, list), f"{label}.finding_ids: list required")
            if isinstance(linked_evidence, list):
                for evidence_id in linked_evidence:
                    collector.require(evidence_id in evidence_ids, f"{label}: unknown evidence ID {evidence_id}")
            if isinstance(linked_findings, list):
                for finding_id in linked_findings:
                    collector.require(finding_id in ledger_by_finding, f"{label}: unknown finding ID {finding_id}")
            if result == "pass":
                collector.require(evidence_state in {"proven", "strongly_supported"}, f"{label}: unknown/inference check cannot be presented as pass")
                collector.require(isinstance(linked_evidence, list) and bool(linked_evidence), f"{label}: pass requires evidence")
                if isinstance(linked_evidence, list):
                    collector.require(not any(eid in evidence_from_error_queries for eid in linked_evidence), f"{label}: error-only evidence cannot support pass")
                if isinstance(linked_findings, list):
                    collector.require(not any(ledger_by_finding.get(fid, {}).get("classification") == "unknown" for fid in linked_findings), f"{label}: unknown finding cannot support pass")
            if evidence_state == "unknown":
                collector.require(result in {"unknown", "not_applicable"}, f"{label}: unknown evidence must remain unknown/not_applicable")

    verdict = report.get("verdict")
    collector.require(isinstance(verdict, dict), "report.verdict: required object")
    if isinstance(verdict, dict):
        collector.require(bool(verdict.get("outcome")), "report.verdict.outcome: required")
        collector.require(bool(verdict.get("text")), "report.verdict.text: required")
        verdict_basis = verdict.get("time_basis")
        collector.require(isinstance(verdict_basis, list) and bool(verdict_basis), "report.verdict.time_basis: non-empty list required")
        if isinstance(verdict_basis, list):
            collector.require(all(item in pin_ids for item in verdict_basis), "report.verdict.time_basis: unknown pin ID")

    ratings = report.get("ratings")
    collector.require(isinstance(ratings, dict), "report.ratings: required object")
    if mode in {"broad", "formal"} and isinstance(ratings, dict):
        for key in RATING_KEYS:
            rating = ratings.get(key)
            collector.require(isinstance(rating, dict), f"report.ratings.{key}: required for {mode} mode")
            if not isinstance(rating, dict):
                continue
            collector.require(rating.get("severity") in {"informational", "low", "medium", "high", "critical", "unknown"}, f"report.ratings.{key}.severity: invalid")
            collector.require(rating.get("likelihood") in {"unlikely", "possible", "likely", "active_or_observed", "not_applicable", "unknown"}, f"report.ratings.{key}.likelihood: invalid")
            collector.require(rating.get("confidence") in {"high", "medium", "low", "unknown"}, f"report.ratings.{key}.confidence: invalid")
            collector.require(bool(rating.get("coverage")), f"report.ratings.{key}.coverage: required")
            basis = rating.get("time_basis")
            collector.require(isinstance(basis, list) and bool(basis), f"report.ratings.{key}.time_basis: non-empty list required")
            collector.require(bool(rating.get("conclusion")), f"report.ratings.{key}.conclusion: required")
            finding_ids = rating.get("finding_ids")
            collector.require(isinstance(finding_ids, list), f"report.ratings.{key}.finding_ids: list required")
            if isinstance(finding_ids, list):
                for finding_id in finding_ids:
                    collector.require(finding_id in ledger_by_finding, f"report.ratings.{key}: unknown finding ID {finding_id}")

    return collector.errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir", type=Path, help="directory containing target-manifest.json, report.json, and evidence-ledger.jsonl")
    parser.add_argument("--json", action="store_true", dest="json_output", help="emit machine-readable validation result")
    args = parser.parse_args(argv)
    errors = validate_case(args.case_dir)
    result = {
        "valid": not errors,
        "error_count": len(errors),
        "errors": errors,
        "scope": "internal consistency only; not RPC honesty, discovery completeness, economic correctness, or protocol safety",
    }
    if args.json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif errors:
        print(f"INVALID: {len(errors)} error(s)")
        for error in errors:
            print(f"- {error}")
    else:
        print("VALID: internal case consistency checks passed")
        print("Passing does not validate RPC honesty, discovery completeness, economic interpretation, or protocol safety.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
