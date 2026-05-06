# Submission Guide

Step-by-step for adding a new plugin entry to Forest Marketplace.

## 1. Fork and branch

```
gh repo fork forest-team/forest-marketplace --clone
cd forest-marketplace
git checkout -b add/my-plugin
```

## 2. Generate the entry

Run the onboarding helper:

```
python3 tools/add-entry.py
```

It prompts for the required fields and writes
`registry/entries/{id}.yaml`. The output will need editing — the helper
is a starting point, not a finisher.

## 3. Fill out the manifest

Open `registry/entries/{id}.yaml` and complete every required field per
[docs/manifest-schema.md](manifest-schema.md). Pay special attention to:

- **`permissions_summary`** — write it for an operator who has never
  seen the plugin. What can it see? What can it change? Where does it
  reach? Plain language, not jargon.
- **`download_sha256`** — leave as `PLACEHOLDER_FILL_AT_RELEASE` until
  you've actually published the `.plugin` artifact, then paste the
  real hash.
- **`contributes.tools[].side_effects`** — be honest. Reviewers WILL
  catch mismatches between this and what the plugin actually does, and
  the PR will be blocked.

## 4. Add to the index

Edit `registry/marketplace.yaml` and append your entry to the `entries`
list:

```yaml
entries:
  - id: soulux-computer-control
    entry: entries/soulux-computer-control.yaml
  - id: my-plugin
    entry: entries/my-plugin.yaml
```

Keep the list alphabetically sorted by `id` to minimize merge conflicts.

## 5. Verify

```
python3 tools/verify-manifest.py
```

Must exit 0 with no errors. Fix anything it flags.

## 6. Run the tests

```
python3 -m pytest tests/
```

## 7. Open a PR

Title: `add: my-plugin v0.1.0`

PR body should include:

- Link to source repo
- Link to release artifact (the `.plugin` file)
- One-paragraph description of what the plugin does
- Confirmation that `permissions_summary` is accurate

## 8. Review

A maintainer will:

1. Run `tools/verify-manifest.py` themselves.
2. Download the `.plugin` payload and verify the SHA-256.
3. Read the `permissions_summary` for accuracy.
4. Add a `reviewed_by` entry on merge.

SLA is 2 weeks. Ping in the issue tracker if it's been longer.
