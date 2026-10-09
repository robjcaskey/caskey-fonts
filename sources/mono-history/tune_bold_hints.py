#!/usr/bin/python3
from hint_tool import hint_tool
from pathlib import Path
import os,subprocess
ROOT=Path(__file__).resolve().parent
TOOL=hint_tool()
env=dict(os.environ)
for mode in ['natural','natural-auto','natural-reference']:
 d=ROOT/'hint-candidates'/mode;d.mkdir(exist_ok=True)
 for style in ['Bold','BoldItalic']:
  src=ROOT/'before-hint-refinement'/f'RobMonoHinted-{style}.ttf'
  opts=['--stem-width-mode=nnn','--increase-x-height=0','--x-height-snapping-exceptions=24-','--hinting-range-min=8','--hinting-range-max=72','--hinting-limit=96','--ttfa-table']
  if mode!='natural-auto': opts += [f'--control-file={ROOT / (style+"-lighter.control")}']
  if mode=='natural-reference': opts += [f'--reference={ROOT / "output" / ("RobMonoHinted-"+("Italic" if style=="BoldItalic" else "Regular")+".ttf")}']
  subprocess.run([str(TOOL),*opts,str(src),str(d/src.name)],env=env,check=True)
