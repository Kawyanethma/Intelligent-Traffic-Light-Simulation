# -*- mode: python ; coding: utf-8 -*-

import os


def _load_env_vars(env_path):
    vals = {}
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith('#') or '=' not in s:
                    continue
                k, v = s.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                vals[k] = v
    except Exception:
        # Silent fallback to defaults if .env missing or malformed
        pass
    return vals


_ROOT = os.path.abspath(os.getcwd())
_ENV = _load_env_vars(os.path.join(_ROOT, '.env'))

_exe_name = _ENV.get('APP_EXE_NAME', 'main')
if _exe_name.lower().endswith('.exe'):
    _exe_name = _exe_name[:-4]

_icon_path = _ENV.get('APP_ICON', os.path.join('installer', 'traffic.ico'))
if not os.path.isabs(_icon_path):
    _icon_path = os.path.join(_ROOT, _icon_path)


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('images', 'images')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=_exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[_icon_path],
)

# After building the one-file EXE, also mirror the images directory into dist/ for packaging needs
import shutil

_src_images = os.path.join(_ROOT, 'images')
_dst_images = os.path.join(_ROOT, 'dist', 'images')
try:
    if os.path.isdir(_src_images):
        os.makedirs(_dst_images, exist_ok=True)
        for root, dirs, files in os.walk(_src_images):
            rel = os.path.relpath(root, _src_images)
            target_dir = os.path.join(_dst_images, rel) if rel != '.' else _dst_images
            os.makedirs(target_dir, exist_ok=True)
            for f in files:
                src_f = os.path.join(root, f)
                dst_f = os.path.join(target_dir, f)
                shutil.copy2(src_f, dst_f)
except Exception:
    # Non-fatal: the EXE already embeds images for one-file mode
    pass
