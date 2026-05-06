# Manifest Schema

This document defines the schema enforced by `tools/verify-manifest.py`.
Every entry in `registry/entries/` MUST satisfy this schema. The
canonical index `registry/marketplace.yaml` references entries by
relative path (see "Index format" below).

## Index format

`registry/marketplace.yaml` looks like:

```yaml
schema_version: 1
entries:
  - id: soulux-computer-control
    entry: entries/soulux-computer-control.yaml
```

The `entry` field is a relative path from `marketplace.yaml`. We chose
include-by-reference over inlining so that:

1. Per-plugin diffs stay small and reviewable.
2. Future tooling can scan one file per plugin without parsing the
   whole index.
3. Multiple maintainers can contribute without merge conflicts on the
   index file.

## Per-entry schema

| Field | Type | Required | Validation |
|---|---|---|---|
| `id` | string | yes | lowercase, hyphens; matches the filename without `.yaml` |
| `name` | string | yes | human-readable display name |
| `version` | string | yes | semver (e.g. `"0.1.0"`) — quoted to preserve string type |
| `author` | string | yes | maintainer handle or org |
| `source_url` | string | yes | URL to source repo |
| `download_url` | string | yes | URL to the `.plugin` payload |
| `download_sha256` | string | yes | SHA-256 hex of the payload (or `PLACEHOLDER_FILL_AT_RELEASE` pre-release) |
| `manifest_signature` | string or null | yes | M6+; `null` for v0.1 entries |
| `description` | string | yes | multi-line description (block scalar OK) |
| `contributes` | object | yes | see "Contributes" below |
| `archetype_tags` | list[string] | no | hints for browse-pane filtering |
| `highest_side_effect_tier` | string | yes | one of `read_only`, `network`, `filesystem`, `external` |
| `required_secrets` | list[string] | no | secret keys the plugin will request at install time |
| `minimum_kernel_version` | string | no | semver version gate |
| `permissions_summary` | string | yes | plain-language summary shown to operators before grant |
| `reviewed_by` | list[object] | no | review trail; each item has `reviewer`, `date`, `verdict` |

## Contributes

The `contributes` object enumerates everything the plugin adds to the
kernel:

```yaml
contributes:
  tools:
    - {name: computer_screenshot, version: "1", side_effects: read_only}
  skills: []
  mcp_servers: []
```

- `tools[].side_effects` MUST be one of `read_only`, `network`,
  `filesystem`, `external` (same enum as `highest_side_effect_tier`).
- `skills` and `mcp_servers` are reserved for future plugin shapes;
  pass empty lists for v0.1.

## Side-effect tier enum

| Tier | Meaning |
|---|---|
| `read_only` | Reads state but does not modify the world (clipboard read, screenshot) |
| `network` | Initiates network IO (web fetch, API call) |
| `filesystem` | Writes to disk under a sandboxed scope |
| `external` | Drives external systems uncontrolled by the kernel (mouse, keyboard, OS app launch) |

The kernel uses `highest_side_effect_tier` for fast filtering and
genre-ceiling enforcement. It MUST equal the max tier across all
`contributes.tools[].side_effects`.

## Strict validation

`tools/verify-manifest.py` enforces:

- All required fields present and of the declared type.
- `highest_side_effect_tier` and each `contributes.tools[].side_effects`
  is in the enum.
- File `id` matches filename stem.
- `manifest_signature` is either `null` or a non-empty string.

Run it from the repo root:

```
python3 tools/verify-manifest.py
```

Exit code 0 means all entries are valid.
