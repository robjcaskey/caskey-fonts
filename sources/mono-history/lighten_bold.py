#!/usr/bin/python3
from hint_tool import hint_tool
"""Reduce bold outlines by 64/2048 em and regenerate embedded hints."""
from pathlib import Path
import ctypes as C
import ctypes.util
import hashlib,json,os,subprocess
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.ttLib.tables.ttProgram import Program
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
class Vector(C.Structure): _fields_=[('x',C.c_long),('y',C.c_long)]
class Outline(C.Structure):
 _fields_=[('n_contours',C.c_short),('n_points',C.c_short),('points',C.POINTER(Vector)),('tags',C.POINTER(C.c_ubyte)),('contours',C.POINTER(C.c_short)),('flags',C.c_int)]
ft=C.CDLL(ctypes.util.find_library('freetype'))
ft.FT_Outline_EmboldenXY.argtypes=[C.POINTER(Outline),C.c_long,C.c_long]
ft.FT_Outline_EmboldenXY.restype=C.c_int
records=[]
for style in ['Bold','BoldItalic']:
 source=ROOT/'before-lighter-bold'/f'RobMonoHinted-{style}.ttf'
 f=TTFont(source);old_metrics=dict(f['hmtx'].metrics)
 for name in f.getGlyphOrder():
  g=f['glyf'][name]
  if g.numberOfContours<=0: continue
  coords,ends,flags=g.getCoordinates(f['glyf'])
  points=(Vector*len(coords))(*(Vector(x*64,y*64) for x,y in coords))
  tags=(C.c_ubyte*len(coords))(*(flag&1 for flag in flags))
  contours=(C.c_short*len(ends))(*ends)
  outline=Outline(len(ends),len(coords),points,tags,contours,0)
  assert ft.FT_Outline_EmboldenXY(C.byref(outline),-64*64,-64*64)==0
  g.coordinates=GlyphCoordinates((round(p.x/64+32),round(p.y/64+32)) for p in points)
  g.program=Program()
 for name in f.getGlyphOrder():
  g=f['glyf'][name]
  g.recalcBounds(f['glyf'])
  advance,lsb=old_metrics[name]
  # Preserve advances, but let the new outline retain its centered position.
  f['hmtx'][name]=(advance,g.xMin if hasattr(g,'xMin') else lsb)
 for tag in ['fpgm','prep','cvt ','TTFA']:
  if tag in f: del f[tag]
 raw=OUT/f'{style}-lighter-unhinted.ttf';f.save(raw)
 control=ROOT/f'{style}-lighter.control'
 control.write_text('latn dflt width 196, 174\n')
 target=OUT/f'RobMonoHinted-{style}.ttf'
 env=dict(os.environ)
 opts=['--stem-width-mode=qqq','--increase-x-height=0','--x-height-snapping-exceptions=24-','--hinting-range-min=8','--hinting-range-max=72','--hinting-limit=96','--ttfa-table',f'--control-file={control}']
 subprocess.run([str(hint_tool()),*opts,str(raw),str(target)],env=env,check=True)
 new=TTFont(target)
 for name,(advance,_) in old_metrics.items(): assert new['hmtx'][name][0]==advance
 new['head'].fontRevision=1.001
 new.save(target);raw.unlink()
 records.append(dict(style=style,reduction_font_units=64,upem=2048,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),options=opts))
(ROOT/'lighter-bold-manifest.json').write_text(json.dumps(records,indent=2)+'\n')
