# tools/

Operator and contributor scripts for the marketplace.

- **`verify-manifest.py`** — Walks `registry/marketplace.yaml` and every
  per-plugin entry under `registry/entries/`, validates each against
  the v0.1 schema (see `docs/manifest-schema.md`), and exits 0 if
  clean, 1 otherwise. Reviewers MUST run this before merging a PR; CI
  also runs it via `tests/test_registry_validity.py`.
- **`add-entry.py`** — Interactive (or argparse-driven) helper that
  scaffolds a new entry under `registry/entries/{id}.yaml`. The output
  needs hand-editing afterward — the helper fills in scaffolding, not
  the substantive fields like `contributes.tools` and
  `permissions_summary`.

Both scripts are zero-dependency aside from PyYAML.
