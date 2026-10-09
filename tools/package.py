#!/usr/bin/env python3
# SPDX-License-Identifier: MIT-0
"""Package the saved, tested designs with public names and complete licenses."""
from pathlib import Path
from fontTools.ttLib import TTFont
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
records=[]
for key,family,prefix,source,license_file in [
 ('caskey-mono','Caskey Mono','RobMonoHinted',ROOT/'sources/mono-history/output','Bitstream-Vera-and-Arev.txt'),
 ('caskey-narrow','Caskey Narrow','RobIosevka550',ROOT/'sources/narrow/output','OFL-1.1.txt')]:
 out=ROOT/'fonts'/key;out.mkdir(parents=True,exist_ok=True)
 license_text=(ROOT/'LICENSES'/license_file).read_text()
 if key=='caskey-mono':
  license_text+='\nCaskey-specific additions, where independently copyrightable, are offered\nunder MIT-0. The upstream conditions above still apply to the combined font.\n\n'+(ROOT/'LICENSES/MIT-0.txt').read_text()
 else:license_text=license_text.replace('\n\nThis Font Software', '\nCopyright (c) 2026 Caskey Fonts contributors\n\nThis Font Software',1)
 (out/'LICENSE.txt').write_text(license_text)
 for style in ['Regular','Bold','Italic','BoldItalic']:
  src=source/(prefix+'-'+style+'.ttf');f=TTFont(src)
  display='Bold Italic' if style=='BoldItalic' else style
  family_ps=family.replace(' ','')
  upstream='DejaVu Sans Mono 2.37; Bitstream Vera; DejaVu contributors; applicable Arev contributions by Tavmjong Bah' if key=='caskey-mono' else 'Iosevka 34.9.0 by Renzhi Li (Belleve Invis)'
  values={1:family,2:display,3:f'{family_ps}-0.1.1-{style}',4:f'{family} {display}',5:'Version 1.011; Caskey Fonts 0.1.1',6:f'{family_ps}-{style}',10:f'Caskey Fonts derivative of {upstream}. See bundled LICENSE.txt and repository ATTRIBUTION.md. No upstream endorsement is implied.',13:license_text,14:'https://github.com/robjcaskey/caskey-fonts/blob/main/LICENSE',16:family,17:display,18:f'{family} {display}',21:family,22:display}
  copyright=f['name'].getDebugName(0) or ''
  values[0]=copyright.rstrip()+'\nCaskey-specific modifications (c) 2026 Caskey Fonts contributors.'
  for id,value in values.items():
   f['name'].removeNames(nameID=id)
   f['name'].setName(value,id,3,1,0x409)
  f['head'].fontRevision=1.011
  # Build diagnostics contain local command paths and are not used to render.
  if 'TTFA' in f:del f['TTFA']
  dest=out/f'{family_ps}-{style}.ttf';f.save(dest)
  original=TTFont(src);check=TTFont(dest)
  for tag in original.keys():
   if tag not in ['GlyphOrder','name','head','TTFA','DSIG']:
    assert original.getTableData(tag)==check.getTableData(tag),(dest,tag)
  assert check['name'].getDebugName(1)==family
  assert check['name'].getDebugName(13)==license_text
  assert original['name'].getDebugName(0).strip() in check['name'].getDebugName(0)
  records.append(dict(file=str(dest.relative_to(ROOT)),source=str(src.relative_to(ROOT)),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),license=license_file))
(ROOT/'fonts/manifest.json').write_text(json.dumps(records,indent=2)+'\n')
print(f'Packaged {len(records)} faces; all rendering tables match their tested sources')
