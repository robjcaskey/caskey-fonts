#!/usr/bin/python3
from pathlib import Path
from fontTools.ttLib import TTFont
import hashlib,json
ROOT=Path(__file__).resolve().parent
src=ROOT/'before-a-foot/RobMonoHinted-Regular.ttf';f=TTFont(src);old=TTFont(src)
g=f['glyf']['a'];changes=[]
# A 10-unit outward tip, with a 2-unit inner-edge move: faint rightward flare.
# Top of the stem and baseline stay fixed; topology and hints are unchanged.
for point,dx in [(13,10),(14,2)]:
 x,y=g.coordinates[point];g.coordinates[point]=(x+dx,y)
 changes.append(dict(point=point,old=[x,y],new=[x+dx,y]))
f['head'].fontRevision=1.008
out=ROOT/'output'/src.name;f.save(out);new=TTFont(out)
assert old['hmtx'].metrics==new['hmtx'].metrics
for n in old.getGlyphOrder():
 if n!='a':assert old['glyf'][n].compile(old['glyf'])==new['glyf'][n].compile(new['glyf'])
assert old['glyf']['a'].program.getBytecode()==new['glyf']['a'].program.getBytecode()
(ROOT/'a-foot-manifest.json').write_text(json.dumps(dict(changes=changes,sha256=hashlib.sha256(out.read_bytes()).hexdigest()),indent=2)+'\n')
print('Added faint rightward regular-a foot flare; advance and hints unchanged')
