# TemporalDenoiser.spec

# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Project root
proj_root = Path(".").resolve()

# Hidden imports (PyInstaller sometimes misses these)
hidden_imports = (
    collect_submodules("numpy")
    + collect_submodules("scipy")
    + collect_submodules("cv2")
    + collect_submodules("rawpy")
    + collect_submodules("imageio")
    + collect_submodules("PySide6")
)

# Resource files (icons, etc.)
datas = collect_data_files("imageio") + [
    ("temporal_denoiser/resources/app_icon.icns", "temporal_denoiser/resources"),
]

# Main app entry point
a = Analysis(
    ["temporal_denoiser/__main__.py"],
    pathex=[str(proj_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["setuptools", "distutils", "pkg_resources", "wheel", "pip", "jaraco"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="TemporalDenoiser",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI app, not terminal
    icon="temporal_denoiser/resources/app_icon.icns",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="TemporalDenoiser",
)

app = BUNDLE(
    coll,
    name="TemporalDenoiser.app",
    icon="temporal_denoiser/resources/app_icon.icns",
    bundle_identifier="com.temporaldnsr.app",
    info_plist={
        "NSHighResolutionCapable": True,
        "CFBundleName": "TemporalDenoiser",
        "CFBundleDisplayName": "TemporalDenoiser",
        "CFBundleShortVersionString": "1.0",
        "CFBundleVersion": "1.0",
    },
)
