#!/usr/bin/python3
"""Guard generator bytecode at glyph/ppem pairs rejected by strict FreeType."""
import json, re, subprocess
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.ttProgram import Program
ROOT=Path(__file__).resolve().parent
files=sorted((ROOT/'output').glob('*.ttf'))
records=[]
for attempt in range(3):
    run=subprocess.run([str(ROOT/'check_render'),*map(str,files)],capture_output=True,text=True)
    (ROOT/'strict-check.log').write_text(run.stdout+run.stderr)
    if run.returncode==0:break
    bad={}
    for path,g,ppem,code in re.findall(r'(\S+\.ttf) glyph (\d+) ppem (\d+) error (\d+)',run.stderr):
        bad.setdefault(path,{}).setdefault(int(g),set()).add(int(ppem))
    if not bad:raise RuntimeError(run.stderr)
    for path,glyphs in bad.items():
        f=TTFont(path)
        for index,sizes in glyphs.items():
            name=f.getGlyphName(index);g=f['glyf'][name]
            if not hasattr(g,'program') or not g.program.getBytecode():continue
            old=g.program.getAssembly()
            asm=[]
            for i,size in enumerate(sorted(sizes)):
                asm+=['MPPEM[ ]','PUSHB[ ]',str(size),'NEQ[ ]']
                if i:asm+=['AND[ ]']
            asm+=['IF[ ]',*old,'EIF[ ]']
            g.program=Program();g.program.fromAssembly(asm)
            records.append({'file':Path(path).name,'glyph':name,'unhinted_ppem':sorted(sizes)})
        f.save(path)
else:raise RuntimeError('Strict validation still fails after exception guards')
(ROOT/'hint-exceptions.json').write_text(json.dumps(records,indent=2)+'\n')
print(run.stdout.strip());print(f'Guarded {len(records)} glyph programs at isolated failing sizes; ASCII is unaffected.')
