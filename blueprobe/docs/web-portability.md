# Passing web observations to Python/Node replacement verification

First organize the saved real observations. No new browser crawling, emoji moving, or HTML fetching is built.
Fetching and interaction stay with browser-test-kit and the existing Flutter collection; completeness of saved artifacts and
coverage of the 215 routes stay with Flutter's existing `python/check_web_observations.py`.

```sh
python -S web_observations.py /path/to/saved-pages --source-root /path/to/flutter_navigation_basic > observed.json
```

Replace `/path/to/saved-pages` with an existing directory where the fetched artifacts were extracted,
and `/path/to/flutter_navigation_basic` with an existing source directory.
The first positional argument is the observation directory, not a subcommand called `saved-pages`.
It reads `web-observation.json` under it recursively. If the source list isn't needed,
`--source-root` can be omitted.

No additional dependencies, Flutter, Dart SDK, Xcode, Android SDK, or browser are needed.
It reads `flutter-web-observation/1` and the adjacent `exploration.json`, and emits `web-portability-observations/1`
following BlueProbe's existing `records / counts / unknown` contract.

- `raw` keeps the observation's source text; `derived` keeps labels, display coordinates, viewport, interaction history, and collection results.
- Missing interaction history is kept as `null` and counts. Invalid coordinates, empty observations, and mixtures of different reported build SHAs are not hidden.
- The source list is paths, sizes, and SHA-256 of Dart/Kotlin/Swift files and the main build settings.
  It excludes generated-artifact directories but includes test sources. File bodies are not executed, converted, or imported.
  File hashes don't prove the mapping between a file and a rendered route, or the runtime version.
- Exit 0 means parsing completed, not that the app passed. Invalid records exit 2.
  Records where the producer failed are also kept and counted in `producer_failed_or_incomplete`.

At this stage, coordinates are rectangles on the viewport at collection time, not a guarantee of click targets on another device.
`reported_build_sha` is also the producer's reported value, not proof of independently executed code.
Byte verification of screenshots is also done by the existing producer verifier.

## Completion conditions per stage

| Check | What runs | What this stage tells you |
|---|---|---|
| Parsing saved observations | This CLI | Recorded structure, coordinates, and interactions, and missing information |
| Replacement's input/output | Python/Node commands specified in xprobe's `contract_probe.py` | Whether each implementation meets the specified expected results for the same input |
| Current web screens | Existing browser-test-kit / Flutter real-browser collection | Actual rendering and behavior for the target version, viewport, and interaction conditions |
| OS permissions and native integration | Dedicated checks on the target platform | Only the capabilities exercised. Not inferred from a web pass |

Features that are self-contained on the web are reduced to contracts that state the feature's input, expected output, state transitions, target routes, and version.
Saved observations are used to find candidates; expected results are not automatically copied and made the answer.
Even if Python and Node return the same wrong answer, it fails if it contradicts the expected result.

**Not implemented / not observed:** backend request/response bodies and state transitions, mapping from source to routes,
source correspondence with the original build, OS side effects, and a Python/Node implementation of the whole app.
These are also kept in `unobserved`. Reproducing the backend needs an ordered I/O contract;
merely replaying logs is not treated as an independent backend implementation.
Reversible Dart↔Kotlin/Swift conversion and full semantic analysis are not part of this CLI.

The first real-data verification parsed the existing 215 saved pages, 2,895 control rectangles, and 645 interactions.
This is a read verification of those saved observations, not a pass count for the current source or native features.
