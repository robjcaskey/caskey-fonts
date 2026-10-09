> Historical design notes from the Ghostty QD experiment. For current names,
> installation and portable builds, see the repository README and BUILD.md.

# Rob Mono Hinted

A separately named derivative of the installed DejaVu Sans Mono family, with
regular, bold, italic (Oblique source), and bold italic faces. The original fonts
are not replaced. Installed under `~/.local/share/fonts/rob-mono-hinted`.

Try `ghostty-qd-font bespoke`; compare with `ghostty-qd-font dejavu-native`.
Both select native embedded hints and retain your current QD rendering settings.
Selecting --qd-hinting=full would bypass these embedded programs; native is
the launcher default as of qd.3.
Restart test windows after rebuilding. This font is not selected globally.

## Original version 1.000 tuning (before lighter bold)

The outlines, advances and line metrics are preserved. This variant does not
narrow the font. ttfautohint 1.8.4 generates TrueType programs, with manually
chosen font-specific controls, rather than hand-writing every glyph program:

- Quantized horizontal-stem alignment in each rasterization mode (`qqq`).
- Latin stem classes measured from H/o: 170/156 font units for regular/italic,
  260/238 for bold/bold italic, preferring the straight crossbar class.
- No extra small-size x-height boost, and no x-height snapping at 24 PPEM and
  above, intended to reduce apparent height inflation at high raster sizes.
- Generated hint sets at 8–72 PPEM; hinting disabled above 96 PPEM.

The hint programs do not encode the QD triangle. Ghostty's private Harmony
renderer applies those sample positions after hinting. These are experimental
choices, not a measured optical optimization or a claim of superior legibility.

## Strict validation and exceptions

Upstream ttfautohint output, including its default untuned output, fails some
FreeType pedantic checks. Ordinary rendering succeeds, but we additionally wrap
those specific glyph programs with size checks so they run without their glyph
instructions at the rejected sizes. The exceptions mostly concern non-ASCII
characters at 19 PPEM, plus a few at 56/72 PPEM. ASCII is unaffected. Composite
components can still use their own hints. Details: `hint-exceptions.json`.
This is an explicit limitation of this first candidate, not hand-tuned hinting
for every writing system.

After these guards, 109,026 glyph/size rasterizations pass with native hinting
and FT_LOAD_PEDANTIC, covering every glyph of all four faces at 14,19,24,28,37,
38,42,56,72 PPEM. The original outline coordinates and metrics compare equal.
At compositor scale 1.5, real Ghostty captures differ by 29,509 pixels between
original and custom native hints. With forced autohinting, the captures match
exactly, demonstrating the difference is from the embedded hints.

## Reproduce

Private extracted Debian packages `ttfautohint` and `libttfautohint1t64` provide
the generator under `tools/extracted`, with LD_LIBRARY_PATH used only for that
build tool, never for Ghostty. Python fontTools renames and validates the fonts.
Source/output hashes and options: `manifest.json`. License: `output/LICENSE-DejaVu.txt`.

1. Compile `check_render.c` with `cc $(pkg-config --cflags freetype2)
   check_render.c -o check_render $(pkg-config --libs freetype2)`.
2. Run `build.py`, then `guard_exceptions.py` under a shared CPU/memory lease.
3. Copy output fonts/license to the private installation directory; run fc-cache
   on that directory. Refresh output hashes in the manifest after guards.
4. Run `scripts/qd/check_font_hints.py` from the worktree under a shared lease.

The qd.2 build also fixes the FreeType flag ABI so full autohinting and native
hinting are distinct. Its focused flag tests pass; the package's unfiltered
suite cannot run because its upstream JetBrainsMono test fixture is absent.

## Lighter bold update

Bold and bold italic now use thinner outlines (revision 1.001); regular and
italic files are byte-identical to the prior installation. `lighten_bold.py`
reduces bold strokes by 64 units per 2048 em using FreeType outline offsets,
recenters them, and regenerates hint programs with horizontal stem classes
196/174. Advances and vertical line metrics remain unchanged; side bearings
follow the centered new outlines. Iosevka 550 is unchanged.

The upright H vertical stem changes from 295 to approximately 231 units:
0.113 em versus Iosevka 550 bold's 0.103 em. This is an outline-based target,
not a promise that different letterforms look exactly equally weighted.
Prior font files are saved under `before-lighter-bold/`; this makes the build
repeatable without accumulating thinning. After rebuilding, run
`guard_exceptions.py` and install only Bold and BoldItalic from `output/`.
The original `build.py` rebuilds the heavier original; follow it with this
lighter-bold step to reproduce the current variant.

Validation: 121,140 native-hinted glyph rasters pass across all four styles
at ten sizes including 32 ppem (16 pt at 150%). Ten regenerated bold glyph
programs needed size-specific guards; no ASCII glyph needed one. Regular
and italic hashes are unchanged; all advances and vertical line metrics
match the previous files. New hashes/options: `lighter-bold-manifest.json`.
Restart a bespoke terminal to load the updated bold faces.

## Bold hint refinement, revision 1.002

The installed bold faces now use natural stem widths (`nnn`) instead of
quantized widths (`qqq`). Stem classes are measured by ttfautohint from the
thinned outlines instead of imposing the earlier 196/174 control values.
Baseline/blue-zone hinting remains enabled; high-size x-height snapping remains
disabled from 24 ppem. This is a hint-only update: every glyph outline, advance,
side bearing and vertical line metric matches the preceding lighter-bold build.
Regular and italic files remain byte-identical, and Iosevka is unchanged.

`tune_bold_hints.py` generates three candidates from the saved
`before-hint-refinement/` snapshot. The selected one is `natural-auto`.
Copy its Bold/BoldItalic to output, run guard_exceptions.py, then install only
those two files. `hint-refinement-manifest.json` records the installed hashes.

Actual Ghostty QD captures at 16 pt / 150% compare original hints, natural
stems with existing controls, automatically measured natural stems, and
regular-font reference zones. `scripts/qd/check_bespoke_pairs.py` tests
rn/nn/mm/mn/nm/sp/ps/st/ts/tt/ft/fi/fl/ffi/Il1/O0, words and mixed-weight
boundaries. Regular text is pixel-identical across candidates. Captures and
results: testing/qd/bespoke-pairs. Visual inspection favored natural-auto;
this does not establish subjective appearance on the physical panel.
Strict validation passes 121,140 glyph/size combinations, with the same ten
size-specific non-ASCII hint guards; no ASCII exceptions.

## Taller lowercase and curved s/l, revision 1.003

Current installed variant raises lowercase x-height approximately 4% in all
four faces. `raise_xheight.py` starts from `before-xheight/` (the preceding
lighter-bold/refined-hint build), so repeated builds do not accumulate changes.
It maps lowercase baseline-to-x-height vertically, tapering the displacement
to zero at cap height; coordinates below baseline stay fixed. Character advances,
side bearings, line metrics and uppercase ASCII outlines remain identical.
Decomposing affected accented glyphs may round fractional component coordinates
by at most half a font unit. The core u/w/m shapes retain their horizontal coordinates.

The upper inner/outer s Bezier handles are shortened to 55% of their prior
length for a rounder top. The l flag gains a quadratic top edge with a 16-unit
control rise, giving an actual 8/2048-em bow (0.125px at 32ppem). Hint programs
for s/l and common accented forms run below 24ppem; at higher resolutions those
glyphs retain their outline curves without grid fitting. Other glyphs retain
full generated hints: regular/italic quantized stems, lighter bold natural stems.

All 121,140 glyph/size checks pass after exception guards. This outline change
exposes more strict ttfautohint failures at 19ppem: 1,656 regular/italic glyphs
need guards there, one also at 72ppem; ten bold glyphs need guards at 72ppem.
These glyphs render without their own glyph instructions at the guarded sizes.
No ASCII failure guards are needed. This is a known limitation at small sizes,
not a claim of individually optimized hinting across the whole character set.
At the current 16pt/150% setting (32ppem), none of these failure guards apply.

Actual QD rendering at 16pt/150% was checked with adjacent u/w/m/n/s/l pairs,
words and mixed weights in `scripts/qd/check_bespoke_xheight.py`; outputs are
in testing/qd/bespoke-xheight. Caps/spacing/metrics are also checked directly.
Reproduce: run raise_xheight.py, guard_exceptions.py, then install the four
output font files and refresh fontconfig. New hashes: xheight-manifest.json.

## Subtle entry accents and e/w refinement, revision 1.005

`pen_entry.py` starts from before-pen-entry/ and appends TrueType point shifts
AFTER existing grid fitting in upright Regular/Bold. Selected lowercase entry
caps (b d f h i j k l m n p q r t u w) gain a small rising cut without shearing
letter bodies or changing advances. At 32ppem the leading cap point moves down
0.25px; the l flag's curve control moves half that. Effects scale with PPEM and
apply only from 24 through 96ppem. Existing italic faces retain their italic
geometry. This accent is part of embedded native hints; force-autohint or
hinting=off bypasses it. Shapes and unrelated glyph programs are unchanged.

`refine_ew.py` starts from before-ew/ (which includes those entry hints).
Bold/BoldItalic e crossbars move down 0.25px at 32ppem after hinting, with nearby
curve controls moved half as far. Regular e is unchanged. The same 24–96ppem
range applies. Lowercase w receives 24/2048-em horizontal outline thickening
in all four styles. Regular w already fills its cell, so it is constrained to
its original 0..1233-unit envelope; bold w uses available side bearings.
Existing italic right overhang does not increase. Advances remain identical;
w side bearings follow its adjusted outline. This is consistent w shaping,
not contextual kerning or borrowing another character's column. Other outline
coordinates and vertical metrics are unchanged.

Both stages pass 121,140 strict native-hint raster checks with no additional
failure guards. Actual QD captures at 16pt/150% verify changed rendering in
entry-stroke pairs and -wa/-w/ww/www/wmw/ewe/ee words and mixed weights.
Scripts: check_bespoke_pen_entry.py and check_bespoke_ew.py under scripts/qd.
Details/hashes: pen-entry-manifest.json and ew-manifest.json. Before snapshots
make each stage reproducible without accumulating shifts. Apply these stages
after the xheight build/guards, then install output fonts and refresh fontconfig.

## Very subtle bold g lower curve, revision 1.006

`round_g.py` starts from before-g-curve/. In Bold/BoldItalic only, the lower
bowl's inner and outer horizontal tangent handles are shortened 15%. This
reduces the flat-looking run while retaining smooth horizontal tangency,
extrema, stroke thickness at the deepest point, and character spacing.
All other glyphs and the existing hint programs are unchanged. Regular and
italic files were not replaced. Hashes/point changes: g-curve-manifest.json.

60,270 glyph/size rasters pass strict native-hint checks for the two faces.
Actual QD rendering at 16pt/150% changes the bold g pairs while regular rows
remain pixel-identical: scripts/qd/check_bespoke_g_curve.py and its captures
under testing/qd/bespoke-g-curve. Restart a bespoke window to load the update.

## Regular l/a refinements, revision 1.008

Regular face only: refine_regular_l.py lowers the l flag's two left endpoints
8 font units (0.125px at 32ppem). Small 4–8 unit shifts of lower-left curve
controls give a trace of italic-like entry while preserving the baseline,
vertical body and existing subtle flag bow. flare_regular_a.py moves the a's
outer right-foot point 10 units and inner point 2 units rightward (about 0.16px
and 0.03px at 32ppem), with the stem top and baseline fixed. Neither changes
advances or glyph hint programs. Bold and italic faces remain untouched.

Each stage has its own before snapshot and manifest. The final regular face
passes 33,770 native-hinted glyph/size checks. Actual QD la/al/aa/all/tall/calm
captures at 16pt/150% confirm the small changes: check_bespoke_regular_la.py.
Installed regular-face hash is in a-foot-manifest.json. To reproduce, apply
refine_regular_l.py then flare_regular_a.py to their saved source snapshots.

## Regular n entry angle, revision 1.009

refine_regular_n.py increases only regular n's post-hint leading cap drop
from 0.25 to 0.375px at 32ppem, adding a further 0.125px of angle. The existing
24–96ppem range is retained. Its stem body, outline coordinates, cell advance,
other glyphs and bold faces are unchanged. Before snapshot: before-n-entry/;
installed hash: n-entry-manifest.json. All 33,770 native-hint glyph/size checks
pass. As with the other entry accents, this uses embedded native hints.
