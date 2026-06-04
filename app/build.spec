# build.spec — PyInstaller config for MTMS
# Build with: pyinstaller build.spec

# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None

# Project root (the folder this .spec sits in)
ROOT = Path(SPECPATH)

# Data files to bundle alongside the .exe
datas = [
    (str(ROOT / "client" / "assets"), "client/assets"),
]

for f in (ROOT / "data").iterdir():
    if f.is_file() and f.name not in ("BangGia.xlsx", "draft.json"):
        datas.append((str(f), "data"))

a = Analysis(
    ["main.py"],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "reportlab.rl_settings",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Toa Hang",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # no console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "client" / "assets" / "MT.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="MTMS",
)
