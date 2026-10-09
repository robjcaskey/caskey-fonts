# Building Caskey Fonts

## Mono

`tools/rebuild_mono.py` works from the included upstream DejaVu 2.37 fonts and
replays the saved design stages in `build/mono/`. It does not overwrite installed
fonts or the packaged release. Dependencies: Python/FontTools, ttfautohint 1.8.4,
FreeType development headers, pkg-config, C compiler. Rendering-library versions
and build timestamps can affect binary hashes; the release manifest records the
actual packaged sources. Do not assume byte-for-byte reproducibility across tools.

After reviewing the output, copy the four rebuilt TTF files to
`sources/mono-history/output/`, then run `python3 tools/package.py`.

## Narrow

Use Iosevka's source at commit `2487637bb71f41b2a66134afd9faa6c316e5a438`
(version 34.9.0):

```sh
git clone https://github.com/be5invis/Iosevka.git build/iosevka
cd build/iosevka
git checkout 2487637bb71f41b2a66134afd9faa6c316e5a438
cp ../../sources/narrow/private-build-plans.toml private-build-plans.toml
npm ci
npm run build -- ttf::CaskeyNarrow --jCmd=2
```

Install ttfautohint 1.8.4 first (or set TTFAUTOHINT_PATH). Follow the upstream
Node version requirements. The original tested build used the same plan with
the historical family name, saved as `historical-build-plan.toml`; the public
plan changes only its naming. The packaged release renames those tested fonts
and verifies unchanged rendering tables instead of rebuilding them needlessly.

## Packaging

Run `python3 tools/package.py` to regenerate the release from the saved source
TTFs. License text is copied beside each family and embedded in name ID 13.
Upstream copyright notices remain in name ID 0, with Caskey attribution added.
Only naming, font revision and the non-rendering TTFA diagnostics table change.
