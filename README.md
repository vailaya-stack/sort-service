# sort-service

## The contracts

The service is written against [`contracts`](https://github.com/vailaya-stack/contracts),
pinned to a release tag in `lakefile.toml` and to that tag's commit in `lake-manifest.json`.

- The pin must be the latest release: `python3 scripts/check_contracts_latest.py`, run by the
  `Contracts` workflow on every pull request and daily.
- A release is tied to a Lean toolchain and a Mathlib revision, so `lean-toolchain` and the
  `mathlib` pin move with it; `python3 scripts/check_pins.py`, run by CI after the build,
  refuses pins that disagree.
- To move to the latest release, run `python3 scripts/upgrade_contracts.py` and then
  `lake update contracts mathlib`. The `Upgrade contracts` workflow does this hourly and
  opens the pull request; opening it needs the repository setting "Allow GitHub Actions to
  create and approve pull requests", without which it only pushes the branch.

To build against a local checkout of the contracts at `../contracts` instead of the pinned
release:

```sh
cp scripts/local-contracts.json .lake/package-overrides.json   # on
rm .lake/package-overrides.json                                # off
```

Lake reads that file on every command and prints nothing about it. It is under `.lake/`,
which Git ignores, so CI always builds the pinned release.
