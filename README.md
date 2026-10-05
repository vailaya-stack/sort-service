# sort-service

## GitHub configuration

To set up your new GitHub repository, follow these steps:

* Under your repository name, click **Settings**.
* In the **Actions** section of the sidebar, click "General".
* Check the box **Allow GitHub Actions to create and approve pull requests**.
* Click the **Pages** section of the settings sidebar.
* In the **Source** dropdown menu, select "GitHub Actions".

After following the steps above, you can remove this section from the README file.

## The contracts

The service is written against [`contracts`](https://github.com/vailaya-stack/contracts),
pinned to a release tag in `lakefile.toml` and to that tag's commit in `lake-manifest.json`.

- The pin must be the latest release: `python3 scripts/check_contracts_latest.py`, run by the
  `Contracts` workflow on every pull request and daily. To move to a release, set `rev` and
  run `lake update contracts`.
- A release is tied to a Lean toolchain and a Mathlib revision. When they moved, move
  `lean-toolchain` and the `mathlib` pin with it; `python3 scripts/check_pins.py`, run by CI
  after the build, refuses pins that disagree.

To build against a local checkout of the contracts at `../contracts` instead of the pinned
release:

```sh
cp scripts/local-contracts.json .lake/package-overrides.json   # on
rm .lake/package-overrides.json                                # off
```

Lake reads that file on every command and prints nothing about it. It is under `.lake/`,
which Git ignores, so CI always builds the pinned release.
