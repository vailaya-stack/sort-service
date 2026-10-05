#!/usr/bin/env python3
"""Move the pin on the contracts to their latest release.

Rewrites the `rev` of the `contracts` requirement in `lakefile.toml`, and moves
`lean-toolchain` and the `mathlib` pin to the ones that release was built on. Run
`lake update contracts mathlib` afterwards to resolve the manifest. Does nothing when
the pin is the latest release already. Run from the package root.

In a GitHub workflow, the release it moved to is the step output `release`.
"""
import os
import pathlib
import re
import subprocess
import tempfile
import tomllib

from check_contracts_latest import latest_release, requirement


def repin(lakefile: str, name: str, rev: str) -> str:
    """`lakefile` with the `rev` of its requirement `name` set to `rev`."""
    block = re.compile(
        rf'(\[\[require\]\]\nname = "{re.escape(name)}"\n(?:(?!\[).*\n)*?rev = ")[^"]*(")'
    )
    repinned, count = block.subn(rf"\g<1>{rev}\g<2>", lakefile)
    if count != 1:
        raise SystemExit(f"lakefile.toml: no `rev` to set in the requirement of {name}")
    return repinned


def main() -> None:
    contracts = requirement("contracts")
    release = latest_release(contracts["git"])
    if contracts.get("rev") == release:
        print(f"contracts are pinned at their latest release, {release}")
        return

    with tempfile.TemporaryDirectory() as checkout:
        subprocess.run(
            ("git", "clone", "--quiet", "--depth", "1", "--branch", release, contracts["git"], checkout),
            check=True,
            capture_output=True,
        )
        released = pathlib.Path(checkout)
        toolchain = (released / "lean-toolchain").read_text()
        theirs = tomllib.loads((released / "lakefile.toml").read_text(encoding="utf-8"))
    mathlib = [dep["rev"] for dep in theirs.get("require", []) if dep["name"] == "mathlib"]

    path = pathlib.Path("lakefile.toml")
    lakefile = repin(path.read_text(encoding="utf-8"), "contracts", release)
    if mathlib:
        lakefile = repin(lakefile, "mathlib", mathlib[0])
    path.write_text(lakefile, encoding="utf-8")
    pathlib.Path("lean-toolchain").write_text(toolchain)

    print(f"contracts moved from {contracts.get('rev')} to {release}, on {toolchain.strip()}")
    if output := os.environ.get("GITHUB_OUTPUT"):
        with open(output, "a", encoding="utf-8") as f:
            f.write(f"release={release}\n")


if __name__ == "__main__":
    main()
