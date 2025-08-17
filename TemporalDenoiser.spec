# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
from PyInstaller.utils.hooks import (
    collect_submodules, collect_data_files, collect_dynamic_libs
)

# --- Collects for key libs ---
pyside6_hidden = collect_submodules("PySide6")
pyside6_datas  = collect_data_files("PySide6")
pyside6_bins   = collect_dynamic_libs("PySide6")
shiboken6_datas = collect_data_files("shiboken6")

cv2_hidden = collect_submodules("cv2")
cv2_bins   = collect_dynamic_libs("cv2")

numpy_bins  = collect_dynamic_libs("numpy")
scipy_bins  = collect_dynamic_libs("scipy")
rawpy_bins  = collect_dynamic_libs("rawpy")
rawpy_datas = collect_data_files("rawpy")
imageio_datas = collect_data_files("imageio")

# Include your app resources (icons, etc.)
proj_root = Path(__file__).parent
app_icon = str(proj_root / "temporal_denoiser" / "resources" / "app_icon.icns")

pkg_resources_dir = proj_root / "temporal_denoiser" / "resources"
extra_datas = []
if pkg_resources_dir.exists():
    # bundle the whole resources dir alongside the package
    extra_datas.append(
        (str(pkg_resources_dir), "temporal_denoiser/resources")
    )

hiddenimports = (
    pyside6_hidden
    + cv2_hidden
    + [
        # PyInstaller sometimes needs these explicitly for scipy:
        "scipy._lib.messagestream",
    ]
)

binaries = (
    pyside6_bins
    + cv2_bins
    + numpy_bins
    + scipy_bins
    + rawpy_bins
)

datas = (
    pyside6_datas
    + shiboken6_datas
    + rawpy_datas
    + imageio_datas
    + extra_datas
)

block_cipher = None

a = Analysis(
    ['temporal_denoiser/__main__.py'],
    pathex=[str(proj_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={
        # ensure essential Qt plugins get bundled
        "qt_plugins": ["platforms", "imageformats", "styles"],
    },
    runtime_hooks=[],
    excludes=[
        "setuptools", "pkg_resources", "distutils", "pip", "wheel", "jaraco"
    ],
    noarchive=False,
)

# One-dir is generally safer on macOS for heavy libs
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TemporalDenoiser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,   # GUI app
)

app = BUNDLE(
    exe,
    name='TemporalDenoiser.app',
    icon=app_icon if Path(app_icon).exists() else None,
    bundle_identifier='com.yourorg.temporaldenoiser',
    info_plist={
        "CFBundleName": "TemporalDenoiser",
        "CFBundleShortVersionString": "1.0",
        "CFBundleVersion": "1.0",
        "NSHighResolutionCapable": True,
        "LSMinimumSystemVersion": "12.0",  # target macOS 12+
    },
)

coll = COLLECT(
    app,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='TemporalDenoiser'
)
