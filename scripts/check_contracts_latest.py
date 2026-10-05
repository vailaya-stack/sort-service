#!/usr/bin/env python3
"""Refuse a pin on the contracts that is not their latest release.

Reads the `contracts` requirement of `lakefile.toml` and lists the `v<major>.<minor>.<patch>`
tags of its repository. Run from the package root.
"""
import pathlib
import re
import subprocess
import sys
import tomllib

TAG = re.compile(r"refs/tags/(v(\d+)\.(\d+)\.(\d+))$")


def main() -> None:
    lakefile = tomllib.loads(pathlib.Path("lakefile.toml").read_text(encoding="utf-8"))
    contracts = [dep for dep in lakefile.get("require", []) if dep["name"] == "contracts"]
    if not contracts:
        sys.exit("lakefile.toml does not require contracts")
    url, pinned = contracts[0]["git"], contracts[0].get("rev")

    listing = subprocess.run(
        ("git", "ls-remote", "--tags", "--refs", url), check=True, capture_output=True, text=True
    ).stdout
    releases = {}
    for line in listing.splitlines():
        if found := TAG.search(line):
            releases[found[1]] = tuple(int(part) for part in found.groups()[1:])
    if not releases:
        sys.exit(f"{url} has no release tag")
    latest = max(releases, key=releases.__getitem__)

    if pinned != latest:
        sys.exit(
            f"contracts are pinned at {pinned}; their latest release is {latest}\n"
            f'set `rev = "{latest}"` in lakefile.toml and run `lake update contracts`'
        )
    print(f"contracts are pinned at their latest release, {latest}")


if __name__ == "__main__":
    main()
