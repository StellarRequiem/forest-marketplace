# Trust Model

Per ADR-0055 Decision 5, the marketplace enforces a **three-layer trust
chain** between a published manifest entry and a running plugin:

```
manifest_signature  ->  download_sha256  ->  plugin-internal manifest
   (who said it)        (what was sent)       (what got installed)
```

## Layer 1 — manifest signature (M6, deferred)

The marketplace maintainer signs each entry with a registered public
key. The kernel verifies the signature against a known-key list before
trusting any other field. **This layer ships in M6.** Until then, every
v0.1 entry has `manifest_signature: null` and the kernel surfaces them
with an `untrusted` badge in the browse pane (M4).

## Layer 2 — payload SHA-256

`download_sha256` MUST equal the SHA-256 of the `.plugin` payload at
`download_url`. The kernel:

1. Fetches the payload.
2. Hashes it.
3. Aborts install if the hash doesn't match.

This catches CDN tampering, mid-flight corruption, and accidental
re-uploads of a different file under the same URL.

## Layer 3 — plugin-internal manifest

The `.plugin` package itself contains a `manifest.yaml` that the kernel
re-parses at install time. It MUST agree with the marketplace entry on:

- `id`
- `version`
- `contributes.tools[].name` and `version`
- `highest_side_effect_tier`

If anything disagrees, the kernel rejects the install. This catches a
maintainer accidentally pointing a marketplace entry at the wrong
artifact.

## What v0.1 actually enforces

| Layer | v0.1 status |
|---|---|
| 1 — manifest signature | **deferred to M6**; `null` allowed |
| 2 — payload SHA-256 | enforced; mismatch aborts install |
| 3 — internal manifest agreement | enforced at install time by the kernel |

So v0.1 catches accidental tampering and maintainer mistakes, but does
NOT defend against a marketplace-repo compromise. M6 closes that gap.

## Operator posture

Operators should treat unsigned entries with the same caution they'd
treat any unsigned download. The kernel's default posture clamps (see
ADR-0048) tighten what an installed plugin can actually DO at runtime,
which is the deeper line of defense regardless of marketplace signing.
