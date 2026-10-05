#!/usr/bin/env python3
"""Refuse dependency pins that disagree. Run after `lake build`, from the package root.

1. Each `rev` that `lakefile.toml` requires is the one `lake-manifest.json` resolved.
   Lake itself only warns when they differ, and builds the old revision.
2. `lean-toolchain` is the one the pinned contracts were released on.
3. Every package the pinned contracts lock (Mathlib and its dependencies) is locked
   at the same revision here, so the contracts are built as they were released.
"""
import json
import pathlib
import sys
import tomllib

CONTRACTS = pathlib.Path(".lake/packages/contracts")


def revisions(manifest: pathlib.Path) -> dict[str, dict]:
    return {p["name"]: p for p in json.loads(manifest.read_text())["packages"]}


def main() -> None:
    problems = []
    lakefile = tomllib.loads(pathlib.Path("lakefile.toml").read_text(encoding="utf-8"))
    locked = revisions(pathlib.Path("lake-manifest.json"))

    for dep in lakefile.get("require", []):
        name, rev = dep["name"], dep.get("rev")
        entry = locked.get(name)
        if entry is None:
            problems.append(f"{name}: required by lakefile.toml, missing from the manifest")
        elif rev is not None and entry.get("inputRev") != rev:
            problems.append(
                f"{name}: lakefile.toml requires {rev}, the manifest resolved "
                f"{entry.get('inputRev')}; run `lake update {name}`"
            )

    if not CONTRACTS.is_dir():
        sys.exit(f"{CONTRACTS} is missing; run `lake build` first")
    ours = pathlib.Path("lean-toolchain").read_text().strip()
    theirs = (CONTRACTS / "lean-toolchain").read_text().strip()
    if ours != theirs:
        problems.append(f"lean-toolchain is {ours}, the pinned contracts use {theirs}")
    for name, entry in revisions(CONTRACTS / "lake-manifest.json").items():
        here = locked.get(name)
        if here is None:
            problems.append(f"{name}: locked by the contracts, missing from the manifest")
        elif here.get("rev") != entry.get("rev"):
            problems.append(
                f"{name}: locked at {here.get('rev')}, the pinned contracts lock {entry.get('rev')}"
            )

    if problems:
        sys.exit("\n".join(problems))
    print(f"pins agree: {len(locked)} packages, {ours}")


if __name__ == "__main__":
    main()
