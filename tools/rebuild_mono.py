#!/usr/bin/env python3
# SPDX-License-Identifier: MIT-0
"""Rebuild all Mono design stages in an isolated build directory."""
from pathlib import Path
import os,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
work=ROOT/'build/mono'
if work.exists():shutil.rmtree(work)
shutil.copytree(ROOT/'sources/mono-history',work)
env=dict(os.environ,DEJAVU_SOURCE_DIR=str(ROOT/'upstream/dejavu-2.37'))
flags=subprocess.check_output(['pkg-config','--cflags','--libs','freetype2'],text=True).split()
subprocess.run(['cc',str(work/'check_render.c'),'-o',str(work/'check_render'),*flags],check=True)
def run(name):subprocess.run([sys.executable,str(work/name)],env=env,check=True)
def snap(name):shutil.copytree(work/'output',work/name,dirs_exist_ok=True)
def guard():run('guard_exceptions.py')
run('build.py');guard();snap('before-lighter-bold')
run('lighten_bold.py');guard();snap('before-hint-refinement')
run('tune_bold_hints.py')
for p in (work/'hint-candidates/natural-auto').glob('*.ttf'):shutil.copy2(p,work/'output'/p.name)
guard();snap('before-xheight')
run('raise_xheight.py');guard();snap('before-pen-entry')
run('pen_entry.py');snap('before-ew')
run('refine_ew.py');snap('before-g-curve')
run('round_g.py');snap('before-regular-l')
run('refine_regular_l.py');snap('before-a-foot')
run('flare_regular_a.py');snap('before-n-entry')
run('refine_regular_n.py');snap('before-r-context')
run('contextual_r.py')
subprocess.run([str(work/'check_render'),*map(str,sorted((work/'output').glob('*.ttf')))],check=True)
print('Rebuilt and validated:',work/'output')
print('Review before replacing sources/mono-history/output and running tools/package.py.')
