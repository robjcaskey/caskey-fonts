# Attribution and provenance

## Caskey Mono

Derived from DejaVu Sans Mono 2.37 (Debian package fonts-dejavu-core 2.37-8),
including its Bold, Oblique and Bold Oblique faces. DejaVu itself builds on
Bitstream Vera. Copyright © 2003 Bitstream, Inc.; DejaVu changes are public domain.
Applicable Arev glyph contributions are copyright © 2006 Tavmjong Bah.

- Project: https://dejavu-fonts.github.io/
- Pinned upstream license: https://github.com/dejavu-fonts/dejavu-fonts/blob/version_2_37/LICENSE
- Original font files and author list: `upstream/dejavu-2.37/`
- Applicable family terms: `LICENSES/Bitstream-Vera-and-Arev.txt`
- Complete upstream distribution license, also including notices for unrelated
  DejaVu Math, retained for reference: `LICENSES/DejaVu-2.37.txt`. No DejaVu Math
  font is included in this project.

Caskey changes include custom/generated hint programs, lighter bold outlines,
4% higher lowercase bodies, rounded s/g, subtle l/a/n details, strengthened w,
and subtle native-hint entry/crossbar adjustments. They are modifications of
upstream work, not a claim to have designed the original typeface.

## Caskey Narrow

Derived from Iosevka 34.9.0, copyright © 2015–2026 Renzhi Li (Belleve Invis).
Upstream commit: `2487637bb71f41b2a66134afd9faa6c316e5a438`.

- Project: https://github.com/be5invis/Iosevka
- Pinned source: https://github.com/be5invis/Iosevka/tree/2487637bb71f41b2a66134afd9faa6c316e5a438
- License: SIL Open Font License 1.1, `LICENSES/OFL-1.1.txt`
- Source build plan: `sources/narrow/private-build-plans.toml`

The custom width is 550 units/em, between stock Iosevka and Liberation Mono.
Regular design weight is 400; bold design weight is 600, exposed as Bold for
normal terminal selection. The project adds no Reserved Font Names.

## Build tools

Hint programs were generated using ttfautohint 1.8.4 by Werner Lemberg and
contributors, based on FreeType. Its explicit generated-bytecode exception
permits copying, distributing and modifying the embedded output without imposing
FTL/GPL on the fonts; see `LICENSES/ttfautohint-COPYING.txt` and
https://github.com/fonttools/ttfautohint/blob/v1.8.4/COPYING .

FontTools and FreeType are external build/validation tools. Their binaries and
source are not vendored here. The local Ghostty QD renderer is a separate project;
these font files do not include its code or promise panel-specific optimization.
