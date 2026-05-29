# build.spec — PyInstaller config for MTMS
# Build with: pyinstaller build.spec

# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None

# Project root (the folder this .spec sits in)
ROOT = Path(SPECPATH)

# Data files to bundle alongside the .exe
# Format: (source_path_on_disk, destination_folder_in_bundle)
datas = [
    (str(ROOT / "data"),                       "data"),
    (str(ROOT / "client" / "assets"),          "client/assets"),
]

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
    name="MTMS",
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
