#!/usr/bin/python3
"""Slightly round the lower bowl of bold g without changing its extrema."""
from pathlib import Path
from fontTools.ttLib import TTFont
import json,hashlib
ROOT=Path(__file__).resolve().parent
records=[]
for style in ['Bold','BoldItalic']:
 src=ROOT/'before-g-curve'/f'RobMonoHinted-{style}.ttf';f=TTFont(src);old=TTFont(src)
 g=f['glyf']['g'];changes=[]
 # Shorten tangent handles 15% at both lower-bowl extrema. Retain horizontal
 # tangents, smooth joins, deepest point and the bowl's stroke thickness there.
 for apex,handles in [(15,[14,16]),(22,[21,23])]:
  x,y=g.coordinates[apex]
  for i in handles:
   cx,cy=g.coordinates[i];assert cy==y and not g.flags[i]&1
   nx=round(x+.85*(cx-x));g.coordinates[i]=(nx,cy)
   changes.append(dict(point=i,old=[cx,cy],new=[nx,cy]))
 f['head'].fontRevision=1.006
 out=ROOT/'output'/src.name;f.save(out);new=TTFont(out)
 assert old['hmtx'].metrics==new['hmtx'].metrics
 for n in old.getGlyphOrder():
  if n!='g':assert old['glyf'][n].compile(old['glyf'])==new['glyf'][n].compile(new['glyf']),n
 assert old['glyf']['g'].program.getBytecode()==new['glyf']['g'].program.getBytecode()
 assert all(getattr(old['glyf']['g'],k)==getattr(new['glyf']['g'],k) for k in ['xMin','xMax','yMin','yMax'])
 records.append(dict(style=style,changes=changes,sha256=hashlib.sha256(out.read_bytes()).hexdigest()))
(ROOT/'g-curve-manifest.json').write_text(json.dumps(records,indent=2)+'\n')
print('Rounded bold g lower-bowl handles; metrics/extrema/other glyphs unchanged')
