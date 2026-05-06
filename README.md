# Forest Marketplace

Curated registry of plug-and-play `.plugin` packages for Forest agents.
Sibling repo to [Forest-Soul-Forge](../Forest-Soul-Forge); lives in its own
repo so policy and review decisions don't gate kernel releases.

See [ADR-0055](../Forest-Soul-Forge/docs/decisions/ADR-0055-agentic-marketplace.md)
for the architectural rationale.

## Layout

```
forest-marketplace/
├── README.md
├── CONTRIBUTING.md
├── registry/
│   ├── marketplace.yaml        # canonical index — kernel fetches this
│   └── entries/                # per-plugin manifest entries
│       └── soulux-computer-control.yaml
├── tools/
│   ├── verify-manifest.py      # operator-side schema verifier
│   ├── add-entry.py            # contributor onboarding helper
│   └── README.md
├── docs/
│   ├── manifest-schema.md      # field-by-field schema reference
│   ├── trust-model.md          # three-layer trust per ADR-0055 Decision 5
│   └── submission-guide.md     # step-by-step for contributors
└── tests/
    └── test_registry_validity.py
```

## v0.1 status

- 1 entry: `soulux-computer-control`
- All entries unsigned — signing pipeline lands in M6
- No browse pane in kernel yet — that's M4
- Operators consume via raw GitHub URL fetched at kernel startup

## How operators use it

The Forest kernel auto-discovers entries by reading the
`FSF_MARKETPLACE_REGISTRIES` environment variable (a comma-separated list of
registry root URLs). It defaults to the raw GitHub URL of this repo's
`registry/marketplace.yaml`.

To override:

```
export FSF_MARKETPLACE_REGISTRIES="https://raw.githubusercontent.com/.../registry/marketplace.yaml,https://my.private/registry.yaml"
```

The kernel then exposes `GET /marketplace/index` (M1) and a browse pane (M4)
that surface entries with `untrusted` badges until M6 ships signature
verification.
