# SPDX-License-Identifier: MIT-0
#!/usr/bin/python3
"""Real GTK/OpenGL Ghostty captures in a private CPU-rendered Sway session."""
import itertools
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/contextual-test'
OUT.mkdir(parents=True, exist_ok=True)
BINARY = Path(os.environ.get('GHOSTTY_QD_BINARY', str(Path.home()/'.local/opt/ghostty-qd/bin/ghostty')))
for mode in ['on','off']:
    (OUT/(mode+'.conf')).write_text('background = 000000\nforeground = ffffff\nfont-size = 16\nfont-family = Caskey Mono\nfont-family-bold = Caskey Mono\nfont-feature = '+('calt' if mode=='on' else '-calt')+'\nwindow-padding-x = 8\nwindow-padding-y = 8\n')
(OUT/'sample.py').write_text('import sys,time\nsys.stdout.write("\\033[?25l\\033[2J\\033[H")\nfor line in ["in inn in in", " r r ar rr", "an nn ni rn", "\\033[1min inn r r ar\\033[0m"]:\n sys.stdout.write(line+"\\r\\n")\nsys.stdout.flush()\ntime.sleep(120)\n')

def wait(predicate, proc, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f'process exited {proc.returncode}')
        value = predicate()
        if value:
            return value
        time.sleep(.15)
    raise TimeoutError('readiness timed out')

def stop(proc):
    if proc.poll() is None:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()

def windows(tree):
    result = [tree] if tree.get('app_id') == 'com.rob.GhosttyQDTest' else []
    for n in tree.get('nodes', []) + tree.get('floating_nodes', []):
        result += windows(n)
    return result

records = []
with tempfile.TemporaryDirectory(prefix='ghostty-qd-test-') as temp:
    runtime = Path(temp)
    runtime.chmod(0o700)
    cfg = runtime / 'sway.conf'
    cfg.write_text('output HEADLESS-1 mode 1920x1080\nseat seat0 fallback true\nxwayland disable\ndefault_border none\nfocus_follows_mouse no\n')
    env = dict(os.environ, XDG_RUNTIME_DIR=str(runtime), WLR_BACKENDS='headless',
               WLR_RENDERER='pixman', WLR_LIBINPUT_NO_DEVICES='1',
               LIBGL_ALWAYS_SOFTWARE='1', GALLIUM_DRIVER='llvmpipe',
               GDK_BACKEND='wayland', GSK_RENDERER='ngl', __EGL_VENDOR_LIBRARY_FILENAMES='/usr/share/glvnd/egl_vendor.d/50_mesa.json', GTK_A11Y='none',
               LP_NUM_THREADS='2')
    for key in ('WAYLAND_DISPLAY', 'DISPLAY', 'SWAYSOCK', 'DBUS_SESSION_BUS_ADDRESS'):
        env.pop(key, None)
    with (OUT / 'sway.log').open('w') as log:
        sway = subprocess.Popen(['sway', '-c', str(cfg)], env=env, stdout=log, stderr=log, start_new_session=True)
        try:
            wait(lambda: list(runtime.glob('sway-ipc*.sock')), sway)
            ipc = next(runtime.glob('sway-ipc*.sock'))
            wayland = next(p for p in runtime.glob('wayland-*') if not p.name.endswith('.lock'))
            env.update(WAYLAND_DISPLAY=wayland.name, SWAYSOCK=str(ipc))
            def tree():
                return json.loads(subprocess.check_output(['swaymsg', '-s', str(ipc), '-t', 'get_tree', '-r'], env=env))
            cases = [('on',1,1), ('off',1,1)]
            for scale in (1.5,):
                subprocess.run(['swaymsg', '-s', str(ipc), f'output HEADLESS-1 scale {scale}'], env=env, check=True, capture_output=True)
                captures = {}
                for mode, strength, chroma in cases:
                    name = f'{scale}-{mode}-{strength}-{chroma}'
                    case_env = dict(env, GHOSTTY_QD_MODE='subpixel', GHOSTTY_QD_HINTING='native', GHOSTTY_QD_STRENGTH=str(strength), GHOSTTY_QD_CHROMA=str(chroma))
                    cmd = ['dbus-run-session', '--', str(BINARY), '--config-default-files=false',
                           f'--config-file={OUT / (mode+".conf")}', '--gtk-single-instance=false',
                           '--class=com.rob.GhosttyQDTest', '--title=QD render test',
                           '--window-decoration=none', '--shell-integration=none',
                           '-e', '/usr/bin/python3', str(OUT / 'sample.py')]
                    with (OUT / f'{name}.log').open('w') as app_log:
                        app = subprocess.Popen(cmd, env=case_env, stdout=app_log, stderr=app_log, start_new_session=True)
                        try:
                            win = wait(lambda: windows(tree()), app)[0]
                            # Only this isolated compositor is controlled by the test.
                            subprocess.run(['swaymsg', '-s', str(ipc), f'[con_id={win["id"]}] fullscreen enable'], env=env, check=True, capture_output=True)
                            time.sleep(2)
                            log_text = (OUT / f"{name}.log").read_text()
                            assert all(s not in log_text for s in ("failed to make GL context", "surface failed to initialize", "shader compilation failure")), log_text[-2000:]
                            path = OUT / f'{name}.png'
                            subprocess.run(['grim', '-o', 'HEADLESS-1', '-s', str(scale), str(path)], env=env, check=True, capture_output=True)
                            im = Image.open(path).convert('RGB')
                            im.load()
                            assert im.size == (1920,1080), im.size
                            assert im.getbbox(), 'blank output'
                            captures[(mode,strength,chroma)] = im
                        finally:
                            stop(app)
                            wait(lambda: not windows(tree()), sway)
                diff=ImageChops.difference(captures[('on',1,1)],captures[('off',1,1)])
                diff.save(OUT/'difference.png')
                box=diff.getbbox()
                assert diff.crop((0,12,1000,50)).getbbox(), 'in did not change pixels'
                assert diff.crop((0,50,1000,85)).getbbox(), 'whitespace r did not change pixels'
                assert not diff.crop((0,126,1920,1080)).getbbox(), 'bold or trailing area changed'
                records.append({'difference_bounds':box,'changed_pixels':sum(any(p) for p in diff.getdata())})
        finally:
            stop(sway)
(OUT / 'results.json').write_text(json.dumps(records, indent=2)+'\n')
print(json.dumps(records, indent=2))
