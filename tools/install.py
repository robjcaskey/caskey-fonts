#!/usr/bin/env python3
# SPDX-License-Identifier: MIT-0
from pathlib import Path
import shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
for key in ['caskey-mono','caskey-narrow']:
    target=Path.home()/'.local/share/fonts'/key
    target.mkdir(parents=True,exist_ok=True)
    for p in (ROOT/'fonts'/key).iterdir():
        if p.suffix=='.ttf' or p.name=='LICENSE.txt':shutil.copy2(p,target/p.name)
    subprocess.run(['fc-cache',str(target)],check=True)
    print('Installed',target)
