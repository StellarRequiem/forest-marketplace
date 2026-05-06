#!/usr/bin/env python3
"""Verify every marketplace entry against the v0.1 schema.

Run from the repo root:

    python3 tools/verify-manifest.py

Exits 0 if all entries are valid; exits 1 with line-by-line errors
otherwise. v0.1 deliberately avoids a jsonschema dependency — the
schema is small enough that hand-rolled checks are clearer than a
dependency footprint.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml


SIDE_EFFECT_TIERS = {"read_only", "network", "filesystem", "external"}

REQUIRED_ENTRY_FIELDS = [
    ("id", str),
    ("name", str),
    ("version", str),
    ("author", str),
    ("source_url", str),
    ("download_url", str),
    ("download_sha256", str),
    ("description", str),
    ("contributes", dict),
    ("highest_side_effect_tier", str),
    ("permissions_summary", str),
]


def repo_root() -> Path:
    """Locate the repo root from this script's path."""
    return Path(__file__).resolve().parent.parent


def validate_index(index_path: Path, errors: list) -> list:
    """Validate registry/marketplace.yaml and return the entry paths."""
    if not index_path.exists():
        errors.append(f"{index_path}: missing")
        return []

    try:
        data = yaml.safe_load(index_path.read_text())
    except yaml.YAMLError as exc:
        errors.append(f"{index_path}: invalid YAML — {exc}")
        return []

    if not isinstance(data, dict):
        errors.append(f"{index_path}: top-level must be a mapping")
        return []

    if data.get("schema_version") != 1:
        errors.append(
            f"{index_path}: schema_version must equal 1 "
            f"(got {data.get('schema_version')!r})"
        )

    entries = data.get("entries")
    if not isinstance(entries, list):
        errors.append(f"{index_path}: 'entries' must be a list")
        return []

    paths = []
    base = index_path.parent
    seen_ids = set()
    for i, ref in enumerate(entries):
        if not isinstance(ref, dict):
            errors.append(f"{index_path}: entries[{i}] must be a mapping")
            continue
        eid = ref.get("id")
        epath = ref.get("entry")
        if not isinstance(eid, str) or not eid:
            errors.append(f"{index_path}: entries[{i}].id missing or not a string")
            continue
        if eid in seen_ids:
            errors.append(f"{index_path}: entries[{i}].id duplicate ({eid!r})")
        seen_ids.add(eid)
        if not isinstance(epath, str) or not epath:
            errors.append(f"{index_path}: entries[{i}].entry missing or not a string")
            continue
        paths.append(base / epath)

    return paths


def validate_entry(entry_path: Path, errors: list) -> None:
    """Validate one per-plugin entry file."""
    if not entry_path.exists():
        errors.append(f"{entry_path}: missing")
        return

    try:
        data = yaml.safe_load(entry_path.read_text())
    except yaml.YAMLError as exc:
        errors.append(f"{entry_path}: invalid YAML — {exc}")
        return

    if not isinstance(data, dict):
        errors.append(f"{entry_path}: top-level must be a mapping")
        return

    # Required fields + types
    for field, ftype in REQUIRED_ENTRY_FIELDS:
        if field not in data:
            errors.append(f"{entry_path}: missing required field '{field}'")
            continue
        if not isinstance(data[field], ftype):
            errors.append(
                f"{entry_path}: field '{field}' must be {ftype.__name__} "
                f"(got {type(data[field]).__name__})"
            )

    # id must match filename stem
    expected_id = entry_path.stem
    if data.get("id") != expected_id:
        errors.append(
            f"{entry_path}: id {data.get('id')!r} does not match filename "
            f"stem {expected_id!r}"
        )

    # manifest_signature: must be present, null OR non-empty string
    if "manifest_signature" not in data:
        errors.append(f"{entry_path}: missing required field 'manifest_signature'")
    else:
        sig = data["manifest_signature"]
        if sig is not None and not (isinstance(sig, str) and sig):
            errors.append(
                f"{entry_path}: manifest_signature must be null or a "
                f"non-empty string"
            )

    # highest_side_effect_tier enum
    tier = data.get("highest_side_effect_tier")
    if isinstance(tier, str) and tier not in SIDE_EFFECT_TIERS:
        errors.append(
            f"{entry_path}: highest_side_effect_tier {tier!r} not in "
            f"{sorted(SIDE_EFFECT_TIERS)}"
        )

    # contributes.tools[].side_effects enum
    contributes = data.get("contributes")
    if isinstance(contributes, dict):
        tools = contributes.get("tools", [])
        if not isinstance(tools, list):
            errors.append(f"{entry_path}: contributes.tools must be a list")
        else:
            for j, tool in enumerate(tools):
                if not isinstance(tool, dict):
                    errors.append(
                        f"{entry_path}: contributes.tools[{j}] must be a mapping"
                    )
                    continue
                for tf in ("name", "version", "side_effects"):
                    if tf not in tool:
                        errors.append(
                            f"{entry_path}: contributes.tools[{j}] missing '{tf}'"
                        )
                se = tool.get("side_effects")
                if isinstance(se, str) and se not in SIDE_EFFECT_TIERS:
                    errors.append(
                        f"{entry_path}: contributes.tools[{j}].side_effects "
                        f"{se!r} not in {sorted(SIDE_EFFECT_TIERS)}"
                    )
        for f in ("skills", "mcp_servers"):
            if f in contributes and not isinstance(contributes[f], list):
                errors.append(f"{entry_path}: contributes.{f} must be a list")


def main() -> int:
    """Walk the registry and emit any validation errors."""
    root = repo_root()
    index_path = root / "registry" / "marketplace.yaml"
    entries_dir = root / "registry" / "entries"

    errors = []

    referenced_paths = validate_index(index_path, errors)

    # Validate every file referenced by the index
    for p in referenced_paths:
        validate_entry(p, errors)

    # Also validate every YAML file in entries/ — catches orphans (file
    # exists but isn't referenced) and entries that are listed but
    # missing.
    if entries_dir.exists():
        on_disk = sorted(entries_dir.glob("*.yaml"))
        referenced_set = {p.resolve() for p in referenced_paths}
        for p in on_disk:
            if p.resolve() not in referenced_set:
                errors.append(
                    f"{p}: present in entries/ but not referenced by "
                    f"registry/marketplace.yaml"
                )
            # Validate even orphans so authors get useful feedback before
            # they wire the entry into the index.
            validate_entry(p, errors)

    if errors:
        print(f"verify-manifest: {len(errors)} error(s)", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    entry_count = len(referenced_paths)
    word = "entry" if entry_count == 1 else "entries"
    print(f"verify-manifest: OK — {entry_count} {word} valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
