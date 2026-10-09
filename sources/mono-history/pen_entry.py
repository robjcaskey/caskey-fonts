#!/usr/bin/python3
"""A slight nib-like entry after grid fitting, without slanting letter bodies."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.ttProgram import Program
import json,hashlib
ROOT=Path(__file__).resolve().parent
records=[]
for style in ['Regular','Bold']:
 src=ROOT/'before-pen-entry'/f'RobMonoHinted-{style}.ttf'
 f=TTFont(src);cm=f.getBestCmap();xh=f['glyf'][cm[ord('x')]].yMax
 chosen={}
 for ch in 'bdfhijklmnpqrtuw':
  name=cm[ord(ch)];g=f['glyf'][name];coords,ends,flags=g.getCoordinates(f['glyf'])
  if ch=='l':
   top=max(y for x,y in coords)
   ctrl=max(range(len(coords)),key=lambda i:coords[i][1])
   assert not flags[ctrl]&1
   neighbors=[ctrl-1,ctrl+1]
   point=min(neighbors,key=lambda i:coords[i][0])
   moves=[(point,32),(ctrl,16)]
  else:
   edges=[];start=0
   for end in ends:
    for i in range(start,end+1):
     j=i+1 if i<end else start
     a,b=coords[i],coords[j]
     # Left-to-right, flat, upper outline edges have ink beneath them.
     if flags[i]&1 and flags[j]&1 and a[1]==b[1] and b[0]>a[0] and a[1]>.75*xh:
      if ch in 'ij' and a[1]>1.15*xh:continue
      edges.append((i,a[1],a[0]))
    start=end+1
   assert edges,ch
   max_y=max(e[1] for e in edges)
   point=min((e for e in edges if e[1]==max_y),key=lambda e:e[2])[0]
   moves=[(point,32)]
  # MPPEM * 32 / 64 gives a 16/64px shift at 32ppem: equivalent
  # to 16 font units in a 2048-em font. No font/body shear occurs.
  asm=g.program.getAssembly()+['MPPEM[ ]','PUSHB[ ]','24','GTEQ[ ]','MPPEM[ ]','PUSHB[ ]','96','LTEQ[ ]','AND[ ]','IF[ ]','PUSHB[ ]','1','SZPS[ ]','SVTCA[0]']
  for point,amount in moves:
   asm+=['PUSHB[ ]','1','SLOOP[ ]','PUSHW[ ]',str(point),'MPPEM[ ]','PUSHB[ ]',str(amount),'MUL[ ]','NEG[ ]','SHPIX[ ]']
  asm+=['EIF[ ]'];g.program=Program();g.program.fromAssembly(asm)
  chosen[ch]=moves
 f['head'].fontRevision=1.004
 f['maxp'].maxStackElements=max(f['maxp'].maxStackElements,16)
 out=ROOT/'output'/src.name;f.save(out)
 old=TTFont(src);new=TTFont(out)
 assert old['hmtx'].metrics==new['hmtx'].metrics
 for n in old.getGlyphOrder():
  assert old['glyf'][n].getCoordinates(old['glyf'])==new['glyf'][n].getCoordinates(new['glyf'])
  if n not in {cm[ord(ch)] for ch in chosen}:
   a=old['glyf'][n];b=new['glyf'][n]
   assert (a.program.getBytecode() if hasattr(a,'program') else b'')==(b.program.getBytecode() if hasattr(b,'program') else b'')
 records.append(dict(style=style,glyph_points=chosen,shift_at_32ppem_px=.25,sha256=hashlib.sha256(out.read_bytes()).hexdigest()))
(ROOT/'pen-entry-manifest.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records,indent=2))
