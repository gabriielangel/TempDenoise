# TemporalDenoiser.spec
# PyInstaller spec file for macOS app bundle
# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os
import glob

# Project root directory
proj_root = Path(".").resolve()

# Dynamically locate rawpy/libraw
rawpy_path = "/usr/local/opt/python@3.10/lib/python3.10/site-packages/rawpy"
libraw_data = []
if os.path.exists(os.path.join(rawpy_path, "libraw")):
    libraw_data = [(os.path.join(rawpy_path, "libraw"), "rawpy/libraw")]

# Dynamically locate libraw dylib
libraw_binaries = [('/usr/local/opt/libraw/lib/libraw.23.dylib', 'rawpy/libraw')]

# Dynamically locate libpython3.10.dylib
libpython_binaries = [('/usr/local/Cellar/python@3.10/3.10.18/Frameworks/Python.framework/Versions/3.10/lib/libpython3.10.dylib', '.')]

# Dynamically locate PySide6 libraries
pyside6_path = "/usr/local/opt/python@3.10/lib/python3.10/site-packages/PySide6"
pyside6_binaries = []
if os.path.exists(pyside6_path):
    pyside6_binaries = [
        (f"{pyside6_path}/libpyside6.abi3.6.5.dylib", "PySide6"),
        (f"{pyside6_path}/libpyside6qml.abi3.6.5.dylib", "PySide6")
    ]
    qt_lib_path = f"{pyside6_path}/Qt/lib"
    if os.path.exists(qt_lib_path):
        pyside6_binaries.append((f"{qt_lib_path}/*", "PySide6/Qt/lib"))

# Collect tifffile data files
tifffile_data = []
if os.path.exists("/usr/local/opt/python@3.10/lib/python3.10/site-packages/tifffile"):
    tifffile_data = collect_data_files("tifffile", include_py_files=False)

# Hidden imports for all required modules
hidden_imports = (
    collect_submodules("PySide6")
    + collect_submodules("PySide6.scripts")
    + collect_submodules("cv2")
    + collect_submodules("scipy")
    + collect_submodules("numpy")
    + collect_submodules("rawpy")
    + collect_submodules("imageio")
    + collect_submodules("imageio.plugins")
    + collect_submodules("tifffile")
    + ["temporal_denoiser.cinemadng", "temporal_denoiser.denoise", "tifffile"]
)

block_cipher = None

a = Analysis(
    ['temporal_denoiser/__main__.py'],
    pathex=['/Users/runner/work/TempDenoise/TempDenoise'],
    binaries=libpython_binaries + libraw_binaries + pyside6_binaries,
    datas=[
        ('/usr/local/opt/python@3.10/lib/python3.10/site-packages/tifffile/*', 'tifffile'),
        ('/usr/local/opt/python@3.10/lib/python3.10/site-packages/PySide6/*', 'PySide6'),
        ('/usr/local/opt/python@3.10/lib/python3.10/site-packages/cv2/*', 'cv2'),
        ('/usr/local/opt/python@3.10/lib/python3.10/site-packages/rawpy/*', 'rawpy'),
        ('/usr/local/opt/python@3.10/lib/python3.10/site-packages/imageio/*', 'imageio'),
        ('temporal_denoiser/resources/app_icon.icns', '.')  # Correct icon path
    ] + libraw_data + tifffile_data,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

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
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch='x86_64',  # Ensure Intel compatibility
    codesign_identity=None,
    entitlements_file=None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TemporalDenoiser'
)

app = BUNDLE(
    coll,
    name='TemporalDenoiser.app',
    icon='temporal_denoiser/resources/app_icon.icns',
    bundle_identifier='com.gabriielangel.TemporalDenoiser',
    info_plist={
        'LSMinimumSystemVersion': '12.0'  # Ensure macOS 12 compatibility
    }
)
