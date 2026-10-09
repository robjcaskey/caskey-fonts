#!/usr/bin/env python3
# SPDX-License-Identifier: MIT-0
"""Verify contextual r/n substitutions and identical advances using HarfBuzz."""
from pathlib import Path
from fontTools.ttLib import TTFont
import ctypes as C,ctypes.util
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'fonts/caskey-mono/CaskeyMono-Regular.ttf'
h=C.CDLL(ctypes.util.find_library('harfbuzz'))
P=C.c_void_p;U=C.c_uint;I=C.c_int
class Info(C.Structure):_fields_=[('codepoint',U),('mask',U),('cluster',U),('var1',U),('var2',U)]
class Pos(C.Structure):_fields_=[('x_advance',I),('y_advance',I),('x_offset',I),('y_offset',I),('var',U)]
for name,args,result in [('hb_blob_create',[C.c_char_p,U,I,P,P],P),('hb_face_create',[P,U],P),('hb_font_create',[P],P),('hb_ot_font_set_funcs',[P],None),('hb_font_set_scale',[P,I,I],None),('hb_buffer_create',[],P),('hb_buffer_add_utf8',[P,C.c_char_p,I,U,I],None),('hb_buffer_guess_segment_properties',[P],None),('hb_shape',[P,P,P,U],None),('hb_buffer_get_glyph_infos',[P,C.POINTER(U)],C.POINTER(Info)),('hb_buffer_get_glyph_positions',[P,C.POINTER(U)],C.POINTER(Pos)),('hb_buffer_destroy',[P],None),('hb_font_destroy',[P],None),('hb_face_destroy',[P],None),('hb_blob_destroy',[P],None)]:
 fn=getattr(h,name);fn.argtypes=args;fn.restype=result
raw=path.read_bytes();blob=h.hb_blob_create(raw,len(raw),0,None,None);face=h.hb_face_create(blob,0);font=h.hb_font_create(face);h.hb_ot_font_set_funcs(font);h.hb_font_set_scale(font,2048,2048)
class Feature(C.Structure):_fields_=[('tag',U),('value',U),('start',U),('end',U)]
off=Feature(int.from_bytes(b'calt','big'),0,0,0xffffffff)
f=TTFont(path);alt=f.getGlyphID('r.entry');base=f.getGlyphID('r');advance=f['hmtx']['r'][0]
nalt=f.getGlyphID('n.afteri');nbase=f.getGlyphID('n')
for text,want in [(' r',[alt]),('  r',[alt]),('\u00a0r',[alt]),('\u2009r',[alt]),('r',[base]),('ar',[base]),('rr',[base,base]),('-r',[base]),('r r',[base,alt]),('a r ar',[alt,base]),('in',[nalt]),('inn',[nalt,nbase]),('an',[nbase]),('n',[nbase]),('ni',[nbase]),(' in r',[nalt,alt])]:
 b=h.hb_buffer_create();data=text.encode();h.hb_buffer_add_utf8(b,data,len(data),0,len(data));h.hb_buffer_guess_segment_properties(b);h.hb_shape(font,b,None,0);count=U();info=h.hb_buffer_get_glyph_infos(b,C.byref(count));pos=h.hb_buffer_get_glyph_positions(b,C.byref(count))
 actual=[info[i].codepoint for i in range(count.value) if info[i].codepoint in [base,alt,nbase,nalt]]
 assert actual==want,(text,actual,want)
 assert all(pos[i].x_advance==advance for i in range(count.value) if info[i].codepoint in [base,alt,nbase,nalt])
 print(repr(text),[f.getGlyphName(i) for i in actual]);h.hb_buffer_destroy(b)
 b=h.hb_buffer_create();h.hb_buffer_add_utf8(b,data,len(data),0,len(data));h.hb_buffer_guess_segment_properties(b);h.hb_shape(font,b,C.byref(off),1)
 info=h.hb_buffer_get_glyph_infos(b,C.byref(count))
 assert all(info[i].codepoint not in [alt,nalt] for i in range(count.value)),text
 h.hb_buffer_destroy(b)
h.hb_font_destroy(font);h.hb_face_destroy(face);h.hb_blob_destroy(blob)
print('All contextual cases and monospaced advances passed')
