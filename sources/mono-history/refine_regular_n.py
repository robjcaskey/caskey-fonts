#!/usr/bin/python3
"""Make the regular n's initial stroke cap very slightly more angled."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.ttProgram import Program
import hashlib,json
ROOT=Path(__file__).resolve().parent
src=ROOT/'before-n-entry/RobMonoHinted-Regular.ttf';old=TTFont(src);f=TTFont(src)
g=f['glyf']['n'];asm=g.program.getAssembly()
index=max(i for i,line in enumerate(asm) if line.startswith('MUL['))
assert asm[index-1]=='32'
asm[index-1]='48' # 0.375px at 32ppem, previously 0.25px.
g.program=Program();g.program.fromAssembly(asm)
f['head'].fontRevision=1.009
out=ROOT/'output'/src.name;f.save(out);new=TTFont(out)
assert old['hmtx'].metrics==new['hmtx'].metrics
for name in old.getGlyphOrder():
 assert old['glyf'][name].getCoordinates(old['glyf'])==new['glyf'][name].getCoordinates(new['glyf'])
 if name!='n':assert old['glyf'][name].compile(old['glyf'])==new['glyf'][name].compile(new['glyf'])
(ROOT/'n-entry-manifest.json').write_text(json.dumps(dict(old_entry_drop_px_at_32ppem=.25,new_entry_drop_px_at_32ppem=.375,sha256=hashlib.sha256(out.read_bytes()).hexdigest()),indent=2)+'\n')
print('Regular n entry accent increased by 0.125px at 32ppem')
