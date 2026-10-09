#!/usr/bin/python3
"""Tiny regular-l flag drop and italic-like lower-left curve entry."""
from pathlib import Path
from fontTools.ttLib import TTFont
import hashlib,json
ROOT=Path(__file__).resolve().parent
src=ROOT/'before-regular-l/RobMonoHinted-Regular.ttf';f=TTFont(src);old=TTFont(src)
g=f['glyf']['l'];changes=[]
# Move both flag left endpoints together to preserve its local thickness.
# Lower-left Bezier control moves leave the upright stem, baseline, and
# bottom horizontal tangent unchanged.
for point,dx,dy in [(11,0,-8),(12,0,-8),(8,-8,0),(7,-4,0),(1,-4,0)]:
 x,y=g.coordinates[point];g.coordinates[point]=(x+dx,y+dy)
 changes.append(dict(point=point,old=[x,y],new=[x+dx,y+dy]))
f['head'].fontRevision=1.007
out=ROOT/'output'/src.name;f.save(out);new=TTFont(out)
assert old['hmtx'].metrics==new['hmtx'].metrics
for n in old.getGlyphOrder():
 if n!='l':assert old['glyf'][n].compile(old['glyf'])==new['glyf'][n].compile(new['glyf'])
assert old['glyf']['l'].program.getBytecode()==new['glyf']['l'].program.getBytecode()
for k in ['ascent','descent','lineGap']:assert getattr(old['hhea'],k)==getattr(new['hhea'],k)
(ROOT/'regular-l-manifest.json').write_text(json.dumps(dict(changes=changes,sha256=hashlib.sha256(out.read_bytes()).hexdigest()),indent=2)+'\n')
print('Updated only regular lowercase l; spacing and hints preserved')
