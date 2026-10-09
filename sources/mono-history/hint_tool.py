# SPDX-License-Identifier: MIT-0
import os,shutil
from pathlib import Path
def hint_tool():
    path=os.environ.get('TTFAUTOHINT_PATH') or shutil.which('ttfautohint')
    if not path: raise RuntimeError('Install ttfautohint 1.8.4 or set TTFAUTOHINT_PATH')
    return Path(path)
