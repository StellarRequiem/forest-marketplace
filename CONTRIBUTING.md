# Contributing to Forest Marketplace

## Submitting a plugin

1. Fork this repo.
2. Run `python3 tools/add-entry.py` and answer the prompts. The script
   writes `registry/entries/{id}.yaml`.
3. Read [docs/manifest-schema.md](docs/manifest-schema.md) and confirm
   every required field is filled correctly. Pay special attention to
   `permissions_summary` — it's what operators see before granting trust.
4. Run `python3 tools/verify-manifest.py` and fix anything it flags.
5. Add your entry to `registry/marketplace.yaml`.
6. Open a PR.

See [docs/submission-guide.md](docs/submission-guide.md) for the long form.

## Review SLA

Reviewers commit to a 2-week SLA on PRs. The review process:

1. Reviewer runs `tools/verify-manifest.py` — must exit 0.
2. Reviewer inspects the `download_url` payload, confirms the
   `download_sha256` matches.
3. Reviewer reads `permissions_summary` for accuracy: does it actually
   describe what the plugin can do?
4. Reviewer adds a `reviewed_by` entry with their handle, date, and verdict.

## Signing

Signing is **not required for v0.1**. M6 of ADR-0055 will introduce the
signing pipeline. When that lands:

- Maintainers register a public key with the marketplace.
- The `manifest_signature` field becomes mandatory for new entries.
- Existing v0.1 entries get a grace period to add signatures.

Until then, kernels surface unsigned entries with an `untrusted` badge so
operators can make an informed call.
