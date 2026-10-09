#!/usr/bin/env python3
# SPDX-License-Identifier: MIT-0
"""Contextual regular r after whitespace and a subtle n entry after i (calt)."""
from pathlib import Path
import copy,hashlib,json
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot
from fontTools.ttLib.tables.ttProgram import Program
ROOT=Path(__file__).resolve().parent
src=ROOT/'before-r-context/RobMonoHinted-Regular.ttf';f=TTFont(src);old=TTFont(src)
name='r.entry';assert name not in f.getGlyphOrder()
g=copy.deepcopy(f['glyf']['r'])
for i,dx in [(12,-10),(13,-4)]:
 x,y=g.coordinates[i];g.coordinates[i]=(x+dx,y)
asm=g.program.getAssembly();i=max(i for i,a in enumerate(asm) if a.startswith('MUL['));assert asm[i-1]=='32';asm[i-1]='48'
g.program=Program();g.program.fromAssembly(asm)
f['glyf'][name]=g;f['hmtx'][name]=f['hmtx']['r'];f.setGlyphOrder(f.getGlyphOrder()+[name] if name not in f.getGlyphOrder() else f.getGlyphOrder())
if 'GDEF' in f and f['GDEF'].table.GlyphClassDef:
 f['GDEF'].table.GlyphClassDef.classDefs[name]=f['GDEF'].table.GlyphClassDef.classDefs.get('r',1)
whitespace=sorted({glyph for cp,glyph in f.getBestCmap().items() if chr(cp).isspace()},key=f.getGlyphID)
def coverage(names):
 c=ot.Coverage();c.glyphs=names;return c
def lookup(kind,sub):
 l=ot.Lookup();l.LookupType=kind;l.LookupFlag=0;l.SubTable=[sub];l.SubTableCount=1;return l
t=f['GSUB'].table
single=ot.SingleSubst();single.mapping={'r':name}
single_index=len(t.LookupList.Lookup);t.LookupList.Lookup.append(lookup(1,single))
context=ot.ChainContextSubst();context.Format=3
context.BacktrackGlyphCount=1;context.BacktrackCoverage=[coverage(whitespace)]
context.InputGlyphCount=1;context.InputCoverage=[coverage(['r'])]
context.LookAheadGlyphCount=0;context.LookAheadCoverage=[]
record=ot.SubstLookupRecord();record.SequenceIndex=0;record.LookupListIndex=single_index
context.SubstCount=1;context.SubstLookupRecord=[record]
context_index=len(t.LookupList.Lookup);t.LookupList.Lookup.append(lookup(6,context));t.LookupList.LookupCount=len(t.LookupList.Lookup)
assert not any(r.FeatureTag=='calt' for r in t.FeatureList.FeatureRecord)
feature=ot.FeatureRecord();feature.FeatureTag='calt';feature.Feature=ot.Feature();feature.Feature.FeatureParams=None;feature.Feature.LookupCount=1;feature.Feature.LookupListIndex=[context_index]
old_features=list(t.FeatureList.FeatureRecord);new_features=sorted(old_features+[feature],key=lambda r:r.FeatureTag)
remap={i:next(j for j,new in enumerate(new_features) if new is row) for i,row in enumerate(old_features)}
new_index=next(j for j,new in enumerate(new_features) if new is feature)
t.FeatureList.FeatureRecord=new_features;t.FeatureList.FeatureCount=len(new_features)
for sr in t.ScriptList.ScriptRecord:
 systems=([sr.Script.DefaultLangSys] if sr.Script.DefaultLangSys else [])+[x.LangSys for x in sr.Script.LangSysRecord]
 for ls in systems:
  ls.FeatureIndex=[remap[i] for i in ls.FeatureIndex]
  if ls.ReqFeatureIndex!=0xffff:ls.ReqFeatureIndex=remap[ls.ReqFeatureIndex]
  if sr.ScriptTag in ['DFLT','latn']:ls.FeatureIndex.append(new_index)
  ls.FeatureIndex.sort();ls.FeatureCount=len(ls.FeatureIndex)
# A restrained serif-like entry on n only following i. Nudge its upper
# portion right 16 units, and give its leading cap a 12-unit left flare.
nname='n.afteri';ng=copy.deepcopy(f['glyf']['n'])
for i,(x,y) in enumerate(ng.coordinates):
 dx=round(16*max(0,min(1,(y-600)/(1165-600))))
 ng.coordinates[i]=(x+dx-(12 if i==12 else 0),y)
f['glyf'][nname]=ng;f['hmtx'][nname]=f['hmtx']['n']
f.setGlyphOrder(old.getGlyphOrder()+[name,nname])
if 'GDEF' in f and f['GDEF'].table.GlyphClassDef:f['GDEF'].table.GlyphClassDef.classDefs[nname]=1
ns=ot.SingleSubst();ns.mapping={'n':nname}
ni=len(t.LookupList.Lookup);t.LookupList.Lookup.append(lookup(1,ns))
nc=ot.ChainContextSubst();nc.Format=3
nc.BacktrackGlyphCount=1;nc.BacktrackCoverage=[coverage(['i'])]
nc.InputGlyphCount=1;nc.InputCoverage=[coverage(['n'])]
nc.LookAheadGlyphCount=0;nc.LookAheadCoverage=[]
nr=ot.SubstLookupRecord();nr.SequenceIndex=0;nr.LookupListIndex=ni
nc.SubstCount=1;nc.SubstLookupRecord=[nr]
nci=len(t.LookupList.Lookup);t.LookupList.Lookup.append(lookup(6,nc))
t.LookupList.LookupCount=len(t.LookupList.Lookup)
feature.Feature.LookupListIndex.append(nci);feature.Feature.LookupCount=2
f['head'].fontRevision=1.011
out=ROOT/'output'/src.name;f.save(out);new=TTFont(out)
for n in old.getGlyphOrder():
 assert old['glyf'][n].compile(old['glyf'])==new['glyf'][n].compile(new['glyf']),n
 assert old['hmtx'][n]==new['hmtx'][n]
assert new['hmtx'][name]==new['hmtx']['r']
assert new['hmtx'][nname]==new['hmtx']['n']
(ROOT/'r-context-manifest.json').write_text(json.dumps(dict(variants=[name,nname],whitespace=whitespace,advance=new['hmtx'][name][0],sha256=hashlib.sha256(out.read_bytes()).hexdigest()),indent=2)+'\n')
print('Added contextual r.entry and n.afteri; base glyphs and cell advances unchanged')
