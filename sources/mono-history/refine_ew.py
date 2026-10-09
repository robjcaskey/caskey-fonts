#!/usr/bin/python3
"""Lower bold e's bar slightly; strengthen w with unchanged cell advances."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.ttLib.tables.ttProgram import Program
import ctypes as C,ctypes.util,json,hashlib
ROOT=Path(__file__).resolve().parent
class Vector(C.Structure): _fields_=[('x',C.c_long),('y',C.c_long)]
class Outline(C.Structure): _fields_=[('n_contours',C.c_short),('n_points',C.c_short),('points',C.POINTER(Vector)),('tags',C.POINTER(C.c_ubyte)),('contours',C.POINTER(C.c_short)),('flags',C.c_int)]
ft=C.CDLL(ctypes.util.find_library('freetype'))
ft.FT_Outline_EmboldenXY.argtypes=[C.POINTER(Outline),C.c_long,C.c_long]
ft.FT_Outline_EmboldenXY.restype=C.c_int
records=[]
for style in ['Regular','Italic','Bold','BoldItalic']:
 src=ROOT/'before-ew'/f'RobMonoHinted-{style}.ttf';f=TTFont(src);original=TTFont(src)
 g=f['glyf']['w'];coords,ends,flags=g.getCoordinates(f['glyf']);xmin=min(x for x,y in coords);xmax=max(x for x,y in coords)
 advance,lsb=f['hmtx']['w']
 points=(Vector*len(coords))(*(Vector(x*64,y*64) for x,y in coords));tags=(C.c_ubyte*len(coords))(*(flag&1 for flag in flags));contours=(C.c_short*len(ends))(*ends)
 outline=Outline(len(ends),len(coords),points,tags,contours,0)
 assert ft.FT_Outline_EmboldenXY(C.byref(outline),24*64,0)==0
 xs=[p.x/64-12 for p in points];low=min(xs);high=max(xs)
 # Expand within spare side bearings. If the original already fills or
 # overhangs its cell, retain its original horizontal envelope.
 lo=min(xmin,max(0,low));hi=max(xmax,min(advance,high))
 g.coordinates=GlyphCoordinates((round(lo+(x-low)*(hi-lo)/(high-low)),y) for x,(_,y) in zip(xs,coords))
 g.recalcBounds(f['glyf']);f['hmtx']['w']=(advance,lsb+g.xMin-xmin)
 if style.startswith('Bold'):
  main=[12,13,14,21,27] if style=='Bold' else [18,19,29,38]
  blend=[15,22,26] if style=='Bold' else [17,20,30,37]
  e=f['glyf']['e'];asm=e.program.getAssembly()+['MPPEM[ ]','PUSHB[ ]','24','GTEQ[ ]','MPPEM[ ]','PUSHB[ ]','96','LTEQ[ ]','AND[ ]','IF[ ]','PUSHB[ ]','1','SZPS[ ]','SVTCA[0]']
  for pts,amount in [(main,32),(blend,16)]:
   for point in pts:asm+=['PUSHB[ ]','1','SLOOP[ ]','PUSHW[ ]',str(point),'MPPEM[ ]','PUSHB[ ]',str(amount),'MUL[ ]','NEG[ ]','SHPIX[ ]']
  asm+=['EIF[ ]'];e.program=Program();e.program.fromAssembly(asm)
 f['head'].fontRevision=1.005
 f['maxp'].maxStackElements=max(16,f['maxp'].maxStackElements)
 out=ROOT/'output'/src.name;f.save(out);new=TTFont(out)
 for n,(width,_) in original['hmtx'].metrics.items():assert new['hmtx'][n][0]==width
 for n in original.getGlyphOrder():
  if n!='w':assert new['glyf'][n].getCoordinates(new['glyf'])==original['glyf'][n].getCoordinates(original['glyf'])
 for k in ['ascent','descent','lineGap']:assert getattr(new['hhea'],k)==getattr(original['hhea'],k)
 records.append(dict(style=style,w_old_bounds=[xmin,xmax],w_new_bounds=[g.xMin,g.xMax],w_stroke_expansion_units=24,e_bar_shift_at_32ppem_px=.25 if style.startswith('Bold') else 0,sha256=hashlib.sha256(out.read_bytes()).hexdigest()))
(ROOT/'ew-manifest.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records,indent=2))
