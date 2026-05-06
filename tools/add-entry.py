#!/usr/bin/env python3
"""Interactive helper that scaffolds a new marketplace entry.

Prompts the contributor for the required fields and writes
`registry/entries/{id}.yaml`. The output is a starting point — the
contributor still needs to edit it (especially `permissions_summary`,
the `contributes.tools` list, and the `download_sha256`).

Usage:
    python3 tools/add-entry.py
    python3 tools/add-entry.py --id my-plugin --name "My Plugin" --author me
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from textwrap import dedent


SIDE_EFFECT_TIERS = ("read_only", "network", "filesystem", "external")


def prompt(label, default=None, override=None):
    """Read a single field from the contributor."""
    if override is not None:
        return override
    suffix = f" [{default}]" if default else ""
    raw = input(f"{label}{suffix}: ").strip()
    if not raw and default is not None:
        return default
    return raw


def repo_root():
    return Path(__file__).resolve().parent.parent


def render_entry(*, plugin_id, name, version, author, source_url,
                 download_url, description, tier):
    """Produce the YAML body for a new entry."""
    return dedent(
        f"""\
        id: {plugin_id}
        name: {name}
        version: "{version}"
        author: {author}
        source_url: {source_url}
        download_url: {download_url}
        download_sha256: PLACEHOLDER_FILL_AT_RELEASE
        manifest_signature: null   # M6 will populate
        description: |
          {description}
        contributes:
          tools: []   # TODO: list every tool with name, version, side_effects
          skills: []
          mcp_servers: []
        archetype_tags: []
        highest_side_effect_tier: {tier}
        required_secrets: []
        minimum_kernel_version: "v0.6"
        permissions_summary: |
          TODO — describe in plain language what this plugin can see and
          do. Operators see this before granting trust; write it for
          someone who has never read your README.
        reviewed_by: []
        """
    )


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--id", help="plugin id (lowercase, hyphens)")
    p.add_argument("--name")
    p.add_argument("--version", default="0.1.0")
    p.add_argument("--author")
    p.add_argument("--source-url")
    p.add_argument("--download-url")
    p.add_argument("--description")
    p.add_argument(
        "--tier",
        choices=SIDE_EFFECT_TIERS,
        help=f"highest_side_effect_tier ({'|'.join(SIDE_EFFECT_TIERS)})",
    )
    return p.parse_args()


def main():
    args = parse_args()

    print("forest-marketplace add-entry — fill in the fields, edit the")
    print("output afterward to complete `contributes.tools` and the")
    print("`permissions_summary`. Press Ctrl+C to bail.")
    print()

    plugin_id = prompt("id (lowercase, hyphens)", override=args.id)
    if not plugin_id:
        print("error: id is required", file=sys.stderr)
        return 1
    name = prompt("name", default=plugin_id, override=args.name)
    version = prompt("version", default="0.1.0", override=args.version)
    author = prompt("author", override=args.author)
    source_url = prompt("source_url", override=args.source_url)
    download_url = prompt("download_url", override=args.download_url)
    description = prompt(
        "description (single line; edit later for prose)",
        override=args.description,
    )
    tier = prompt(
        f"highest_side_effect_tier ({'|'.join(SIDE_EFFECT_TIERS)})",
        default="read_only",
        override=args.tier,
    )
    if tier not in SIDE_EFFECT_TIERS:
        print(
            f"error: tier must be one of {SIDE_EFFECT_TIERS}",
            file=sys.stderr,
        )
        return 1

    body = render_entry(
        plugin_id=plugin_id,
        name=name,
        version=version,
        author=author,
        source_url=source_url,
        download_url=download_url,
        description=description,
        tier=tier,
    )

    out_path = repo_root() / "registry" / "entries" / f"{plugin_id}.yaml"
    if out_path.exists():
        print(f"error: {out_path} already exists; refusing to overwrite", file=sys.stderr)
        return 1
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body)

    print()
    print(f"wrote {out_path}")
    print("next steps:")
    print(f"  1. edit {out_path} — fill in contributes.tools and permissions_summary")
    print("  2. add the entry to registry/marketplace.yaml")
    print("  3. run python3 tools/verify-manifest.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
