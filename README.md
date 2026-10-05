# sort-service

The sort service of vailaya-stack, in Lean 4 with Mathlib, written against
[`contracts`](https://github.com/vailaya-stack/contracts).

## Where files go

| File | Module | Holds |
|---|---|---|
| `src/SortService.lean` | `SortService` | Only imports: one line per file below. |
| `src/SortService/API.lean` | `SortService.API` | The service and the proof that it meets its contract. |

A file `src/SortService/A/B.lean` is the module `SortService.A.B`, and another file imports it with
`import SortService.A.B`. `lake build` compiles every `.lean` file under `src/SortService/`, whether or not
`src/SortService.lean` imports it. A `.lean` file anywhere else, such as directly in `src/` or at the
top of the repository, belongs to no library: Lake does not compile it and nothing can import
it.

The contracts are imported by their own module names: `import Contracts.SortService`.

## Working locally

Open the `sort-service` folder itself in the editor, not its parent, so Lean finds `lean-toolchain` and
`lakefile.toml`.

```sh
lake exe cache get                  # once per clone: download Mathlib's build
lake build                          # compile everything; errors show here
lake lean src/SortService/API.lean     # compile one file
python3 scripts/check_pins.py       # the pin check CI runs after the build
python3 scripts/check_contracts_latest.py   # the check that the pin is the latest release
```

### Against a local checkout of the contracts

By default the service builds the released contracts it pins. To build the `contracts` folder
next to this one instead, as it is on disk with uncommitted changes included:

```sh
cp scripts/local-contracts.json .lake/package-overrides.json   # on
lake build
rm .lake/package-overrides.json                                # off
lake build
```

- The override expects the folder at `../contracts`.
- Lake prints nothing about it. `ls .lake/package-overrides.json` tells whether it is on.
- In the editor, run "Lean 4: Server: Restart Server" after turning it on or off.
- It is under `.lake/`, which Git ignores, so CI always builds the pinned release. A pull
  request here passes only once the contracts it needs are released.

### Moving to a new release of the contracts

```sh
python3 scripts/upgrade_contracts.py   # move the pins in lakefile.toml and lean-toolchain
lake update contracts mathlib          # resolve them into lake-manifest.json
lake build
```

## The contracts

The service pins a release of the contracts by its tag in `lakefile.toml`, and that tag's
commit in `lake-manifest.json`.

- The pin must be the latest release. The `Contracts` workflow checks it on every pull request
  and daily, so a pull request here goes red when the contracts release until the pin moves.
- A release is tied to a Lean toolchain and a Mathlib revision, so `lean-toolchain` and the
  `mathlib` pin move with it. CI refuses pins that disagree.
- The `Upgrade contracts` workflow checks hourly, moves the pins and pushes a branch
  `contracts-v<version>`. It opens the pull request too when the repository setting "Allow
  GitHub Actions to create and approve pull requests" is on.
