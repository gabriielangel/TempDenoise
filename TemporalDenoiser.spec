# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path
from PyInstaller.utils.hooks import (
    collect_submodules, collect_data_files, collect_dynamic_libs
)

# --- Collects for key libs ---
pyside6_hidden   = collect_submodules("PySide6")
pyside6_datas    = collect_data_files("PySide6")
pyside6_bins     = collect_dynamic_libs("PySide6")
shiboken6_datas  = collect_data_files("shiboken6")

cv2_hidden       = collect_submodules("cv2")
cv2_bins         = collect_dynamic_libs("cv2")

numpy_bins       = collect_dynamic_libs("numpy")
scipy_bins       = collect_dynamic_libs("scipy")

rawpy_bins       = collect_dynamic_libs("rawpy")
rawpy_datas      = collect_data_files("rawpy")

imageio_datas    = collect_data_files("imageio")

# --- Safe project root (works in CI where __file__ may be undefined) ---
proj_root = Path(os.getcwd())

# --- App resources ---
app_icon = str(proj_root / "temporal_denoiser" / "resources" / "app_icon.icns")

a = Analysis(
    ["temporal_denoiser/__main__.py"],
    pathex=[str(proj_root)],
    binaries=(pyside6_bins + cv2_bins + numpy_bins + scipy_bins + rawpy_bins),
    datas=(pyside6_datas + shiboken6_datas + rawpy_datas + imageio_datas),
    hiddenimports=(pyside6_hidden + cv2_hidden),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["setuptools", "distutils", "pkg_resources", "wheel", "pip", "jaraco"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
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
    console=False,
    icon=app_icon,
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
    bundle_identifier="com.example.temporaldenoiser",
    icon=app_icon,
    info_plist={
        "CFBundleName": "TemporalDenoiser",
        "CFBundleDisplayName": "TemporalDenoiser",
        "CFBundleShortVersionString": "1.0",
        "CFBundleVersion": "1.0",
        "NSHighResolutionCapable": "True",
    },
)
