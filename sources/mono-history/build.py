#!/usr/bin/python3
from hint_tool import hint_tool
"""Build a separately named DejaVu Sans Mono derivative with embedded hints."""
from pathlib import Path
from fontTools.ttLib import TTFont
import hashlib, json, os, shutil, subprocess
ROOT = Path(__file__).resolve().parent
SOURCE = Path(os.environ.get('DEJAVU_SOURCE_DIR', ROOT.parents[1] / 'upstream/dejavu-2.37'))
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
TOOL = hint_tool()
env = dict(os.environ)
FAMILY = 'Rob Mono Hinted'
styles = [('Regular', '', [170,156]), ('Bold','-Bold',[260,238]),
          ('Italic','-Oblique',[170,156]), ('Bold Italic','-BoldOblique',[260,238])]
records=[]
for style,suffix,widths in styles:
    source=SOURCE/f'DejaVuSansMono{suffix}.ttf'
    tag=style.replace(' ','')
    control=ROOT/f'{tag}.control'
    control.write_text('# Horizontal stem classes, measured from DejaVu Sans Mono H/o.\n'
                       '# Prefer straight crossbar thickness, retain the curved stem class.\n'
                       + 'latn dflt width ' + ', '.join(map(str,widths)) + '\n')
    raw=OUT/f'{tag}-raw.ttf'
    opts=['--stem-width-mode=qqq','--increase-x-height=0',
          '--x-height-snapping-exceptions=24-', '--hinting-range-min=8',
          '--hinting-range-max=72','--hinting-limit=96','--ttfa-table',
          f'--control-file={control}']
    subprocess.run([str(TOOL),*opts,str(source),str(raw)],env=env,check=True)
    f=TTFont(raw);original=TTFont(source)
    # Keep the source's spacing and vertical layout metrics exactly.
    for table in ('hmtx','hhea','OS/2'):
        f[table]=original[table]
    # Retain legal/attribution records, replace identifying names on all platforms.
    names={1:FAMILY,2:style,3:f'RobMonoHinted-1.000-{tag}',
           4:f'{FAMILY} {style}',5:'Version 1.000; custom hint experiment',
           6:f'RobMonoHinted-{tag}',16:FAMILY,17:style,
           18:f'{FAMILY} {style}',21:FAMILY,22:style}
    for rec in list(f['name'].names):
        if rec.nameID in names: f['name'].removeNames(nameID=rec.nameID,platformID=rec.platformID,platEncID=rec.platEncID,langID=rec.langID)
    for name_id,value in names.items():
        f['name'].setName(value,name_id,3,1,0x409)
        f['name'].setName(value,name_id,1,0,0)
    f['head'].fontRevision=1.0
    target=OUT/f'RobMonoHinted-{tag}.ttf'
    f.save(target);raw.unlink()
    # Ensure tuning has not modified outlines or character advances.
    f=TTFont(target)
    assert f['hmtx'].metrics==original['hmtx'].metrics
    assert f['hhea'].ascent==original['hhea'].ascent and f['hhea'].descent==original['hhea'].descent
    changed=0
    for name in original.getGlyphOrder():
        a=original['glyf'][name];b=f['glyf'][name]
        assert a.getCoordinates(original['glyf']) == b.getCoordinates(f['glyf']),name
        old=bytes(a.program.getBytecode()) if hasattr(a,'program') else b''
        new=bytes(b.program.getBytecode()) if hasattr(b,'program') else b''
        changed+=old!=new
    assert changed>100
    records.append(dict(style=style,source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                        output=target.name,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                        changed_glyph_programs=changed,stem_widths=widths,options=opts))
(ROOT/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
shutil.copyfile(SOURCE / 'LICENSE.txt',OUT/'LICENSE-DejaVu.txt')
print(json.dumps([{'style':r['style'],'changed_glyph_programs':r['changed_glyph_programs']} for r in records],indent=2))
