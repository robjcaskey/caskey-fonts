# Caskey Fonts

Two personal terminal font families, tuned through close reading at 16 pt on a
150%-scaled display. Ready-to-use TrueType files are in [`fonts/`](fonts/).

| Family | Based on | Character |
|---|---|---|
| **Caskey Mono** | DejaVu Sans Mono 2.37 | Fuller lowercase, lighter bold, subtle curves and pen-like entry details |
| **Caskey Narrow** | Iosevka 34.9.0 | Intermediate 550-unit width, regular weight 400 and lighter bold design weight 600 |

Each includes regular, italic, bold and bold italic. Caskey Mono was previously
called **Rob Mono Hinted** / `bespoke`; Caskey Narrow was **Rob Iosevka 550**.
The initial rename preserved every rendering table of the saved, tested fonts.
Later releases include the refinements documented below.

## Install

On Linux, from the repository:

```sh
python3 tools/install.py
```

Choose `Caskey Mono` or `Caskey Narrow` in your terminal. For the locally configured
Ghostty QD launcher:

```sh
ghostty-qd-font caskey-mono
ghostty-qd-font caskey-narrow
```

The legacy `bespoke` and `iosevka-550` aliases continue to work on the original
machine. Those launcher commands require the separate Ghostty QD project; this
repository installs ordinary fonts usable in other applications too.

## Rendering and design

Caskey Mono retains monospaced advances. Lowercase bodies are about 4% taller;
bold has been lightened, with more natural stem hinting. Selected letters have
small bespoke details: a rounder `s` and bold `g`, gently curved `l` flag,
regular `a` foot flare, stronger `w`, and an understated `n` entry angle.

Version 0.1.1 adds two regular-face contextual alternates through OpenType `calt`:
* After whitespace, `r` has a slightly stronger angled entry and tighter upper join.
* In `in`, the `n` has a tiny serif-like entry flare, with its upper outline shifted
  right by up to 16/2048 em. Other `n` combinations retain the original outline.

Both keep the same character advance. Context must be in the same shaping run;
a line start alone does not trigger the whitespace alternate, and style/cursor
boundaries can interrupt context. Disable with `font-feature = -calt` in Ghostty.
The bold and italic faces retain their existing designs.

Some fine accents are encoded in **native TrueType hint programs**, active at
24–96 pixels/em. Force-autohinting or disabling hints bypasses those accents.
At 16 pt, 96 logical DPI and 150% scaling, the font is 32 pixels/em. The regular
and italic `s`/`l` curve treatment avoids grid fitting at 24+ pixels/em.

These are experimental visual choices, not a claim of measured legibility or
an independently designed original typeface. QD subpixel geometry belongs to
the separate renderer, not these font files. The fonts also work in grayscale.

## Build and history

Requires Python 3 and FontTools (`python3 -m pip install -r requirements.txt`).

* `python3 tools/package.py` packages the checked-in tested designs under their
  public names, adds complete licensing metadata, and verifies that the rendering
  tables are unchanged. It writes `fonts/manifest.json` with hashes.
* `python3 tools/rebuild_mono.py` rebuilds all Mono stages in `build/mono/` from
  included DejaVu sources. It also needs ttfautohint 1.8.4, FreeType development
  headers, `pkg-config` and a C compiler. Set `TTFAUTOHINT_PATH` if needed.
* Narrow's pinned source and rebuild instructions: [BUILD.md](BUILD.md).
* `sources/mono-history/` preserves the iterative design scripts, source
  snapshots, controls and manifests. Its README is historical lab documentation;
  old local paths there describe the original experiment, not build requirements.
* Font names, licenses and provenance: [ATTRIBUTION.md](ATTRIBUTION.md).

The source snapshots are intentional: they allow individual refinements to be
reproduced without accumulating outline changes on every run.

## Validation and limits

The portable full Mono rebuild and the original build passed 121,140 strict FreeType glyph/size raster checks
across ten pixel sizes. Subsequent regular-only checks passed 33,770 cases;
bold-only checks passed 60,270. Letter pairs and mixed-weight text were also
captured in the actual Ghostty QD renderer at 16 pt / 150% scaling.

The contextual release passed 33,790 strict native-hint raster checks. HarfBuzz
checks cover positive and negative contexts and fixed advances (`python3
tools/check_contextual_r.py`). An actual Ghostty QD capture at 16 pt / 150% with
`calt` on versus off confirmed changed regular `in` and whitespace-`r` pixels;
the bold sample was unchanged. These checks confirm rendering, not a subjective
improvement in readability.

Some generated non-ASCII hint programs require size-specific guards, chiefly
at 19 pixels/em. They render without their own glyph instructions at those
sizes. No such failure guards apply at 32 pixels/em; some `s`/`l` hints are
intentionally bypassed there to preserve their curves. See the historical
README and `hint-exceptions.json` for details. This is not exhaustive validation
on every operating system, renderer or display.

## License

**The two font families have different upstream licenses.** Caskey Mono retains
Bitstream Vera / applicable Arev conditions; Caskey Narrow remains under SIL OFL
1.1. Our independent tooling is MIT-0, and no new Reserved Font Names or extra
Caskey-specific attribution conditions are imposed. The combined fonts cannot
be relabeled as MIT/public domain or sold by themselves contrary to upstream
terms. Read [LICENSE](LICENSE) and the license beside each family.
