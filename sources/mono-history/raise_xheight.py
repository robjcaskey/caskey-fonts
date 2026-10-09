#!/usr/bin/python3
from hint_tool import hint_tool
"""Raise lowercase x-height 4%, with fixed baseline/cap height/advances."""
from pathlib import Path
import hashlib,json,os,subprocess,unicodedata
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph,GlyphCoordinates
from fontTools.ttLib.tables.ttProgram import Program
ROOT=Path(__file__).resolve().parent
records=[]
for style in ['Regular','Italic','Bold','BoldItalic']:
 src=ROOT/'before-xheight'/f'RobMonoHinted-{style}.ttf'
 f=TTFont(src); original=TTFont(src);cm=f.getBestCmap()
 xheight=f['glyf'][cm[ord('x')]].yMax
 cap=f['glyf'][cm[ord('H')]].yMax
 rise=round(xheight*.04)
 lower={name for cp,name in cm.items() if unicodedata.category(chr(cp))=='Ll'}
 def move(y):
  if y<=0 or y>=cap:return y
  if y<=xheight:return round(y*(xheight+rise)/xheight)
  return round(y+rise*(cap-y)/(cap-xheight))
 # Shorten the horizontal Bezier handles at the two upper s extrema.
 # This rounds its upper bowl without moving its top/baseline or changing width.
 sg=original['glyf'][cm[ord('s')]]
 coords=sg.coordinates
 advance=original['hmtx'][cm[ord('s')]][0]
 for i in range(len(coords)):
  x,y=coords[i]
  if not (sg.flags[i]&1 and .35*advance<x<.7*advance and y>.8*xheight):continue
  for j in [(i-1)%len(coords),(i+1)%len(coords)]:
   cx,cy=coords[j]
   if not sg.flags[j]&1 and cy==y:coords[j]=(round(x+.55*(cx-x)),cy)
 # Add a very shallow quadratic bow to the top flag of lowercase l.
 # Its 16-unit control rise produces an 8-unit (~0.125px at 32ppem) bow.
 lg=original['glyf'][cm[ord('l')]]
 top=max(y for x,y in lg.coordinates)
 for i in range(len(lg.coordinates)-1):
  a,b=lg.coordinates[i],lg.coordinates[i+1]
  if a[1]==top and b[1]==top and lg.flags[i]&1 and lg.flags[i+1]&1:
   points=list(lg.coordinates);points.insert(i+1,(round((a[0]+b[0])/2),top+16))
   lg.coordinates=GlyphCoordinates(points);lg.flags.insert(i+1,0)
   lg.endPtsOfContours=[end+1 if end>=i+1 else end for end in lg.endPtsOfContours]
   break
 else:raise RuntimeError('No top flag segment found for '+style)
 # Snapshot coordinates before modifying any component. Flatten composites to
 # prevent a shared lowercase component from changing an unrelated glyph.
 geometry={n:original['glyf'][n].getCoordinates(original['glyf']) for n in original.getGlyphOrder()}
 for n in original.getGlyphOrder():
  old=original['glyf'][n]
  def affected_component(name):
   glyph=original['glyf'][name]
   return name in lower or (glyph.isComposite() and any(affected_component(c.glyphName) for c in glyph.components))
  if n not in lower and not (old.isComposite() and affected_component(n)):continue
  coords,ends,flags=geometry[n]
  g=Glyph();g.numberOfContours=len(ends)
  if len(ends):
   g.coordinates=GlyphCoordinates((x,move(y) if n in lower else y) for x,y in coords)
   g.endPtsOfContours=list(ends);g.flags=flags
  f['glyf'][n]=g
 for n in f.getGlyphOrder():
  f['glyf'][n].removeHinting()
 for tag in ['fpgm','prep','cvt ','TTFA']:
  if tag in f: del f[tag]
 if hasattr(f['OS/2'],'sxHeight'):f['OS/2'].sxHeight=xheight+rise
 raw=ROOT/'output'/f'{style}-xheight-raw.ttf';f.save(raw)
 mode='nnn' if style.startswith('Bold') else 'qqq'
 opts=[f'--stem-width-mode={mode}','--increase-x-height=0','--x-height-snapping-exceptions=24-','--hinting-range-min=8','--hinting-range-max=72','--hinting-limit=96','--ttfa-table']
 if not style.startswith('Bold'):
  control=ROOT/f'{style}-xheight.control';control.write_text('latn dflt width 170, 156\n')
  opts.append(f'--control-file={control}')
 out=ROOT/'output'/src.name
 env=dict(os.environ)
 subprocess.run([str(hint_tool()),*opts,str(raw),str(out)],env=env,check=True)
 after=TTFont(out);after['head'].fontRevision=1.003
 # Preserve the s and l curves at high resolution; retain its generated hints below
 # 24 ppem. Other letters retain their full embedded hint programs.
 for cp in [ord('s'),0x015b,0x015d,0x015f,0x0161,0x0219,ord('l'),0x013a,0x013c,0x013e,0x0142]:
  name=after.getBestCmap().get(cp)
  if not name:continue
  g=after['glyf'][name]
  if hasattr(g,'program') and g.program.getBytecode():
   asm=['MPPEM[ ]','PUSHB[ ]','24','LT[ ]','IF[ ]',*g.program.getAssembly(),'EIF[ ]']
   g.program=Program();g.program.fromAssembly(asm)
 after.save(out);raw.unlink()
 after=TTFont(out)
 assert after['hmtx'].metrics==original['hmtx'].metrics
 for n in original.getGlyphOrder():
  before,ends,flags=geometry[n];coords,newends,newflags=after['glyf'][n].getCoordinates(after['glyf'])
  assert len(coords)==len(before),n
  assert all(abs(x-a)<=0.5 and abs(y-(move(b) if n in lower else b))<=0.5 for (x,y),(a,b) in zip(coords,before)),n
 for k in ['ascent','descent','lineGap']:assert getattr(after['hhea'],k)==getattr(original['hhea'],k)
 records.append(dict(style=style,old_xheight=xheight,new_xheight=xheight+rise,cap_height=cap,lowercase_glyphs=len(lower),options=opts,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest()))
(ROOT/'xheight-manifest.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records,indent=2))
