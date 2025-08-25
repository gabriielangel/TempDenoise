# TemporalDenoiser.spec
# PyInstaller spec file for macOS app bundle
# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os

# Project root directory
proj_root = Path(".").resolve()

# Dynamically locate rawpy/libraw
rawpy_path = "/usr/local/opt/python@3.10/lib/python3.10/site-packages/rawpy"
libraw_data = []
if os.path.exists(os.path.join(rawpy_path, "libraw")):
    libraw_data = [(os.path.join(rawpy_path, "libraw"), "rawpy/libraw")]

# Collect tifffile data files
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
    binaries=[
        ('/usr/local/opt/python@3.10/lib/libpython3.10.dylib', '.'),
        ('/usr/local/opt/libraw/lib/libraw.20.dylib', 'rawpy/libraw'),
        ('/usr/local/opt/python@3.10/lib/python3.10/site-packages/PySide6/Qt/lib/QtCore.framework/Versions/A/QtCore', 'PySide6/Qt/lib'),
        ('/usr/local/opt/python@3.10/lib/python3.10/site-packages/PySide6/Qt/lib/QtGui.framework/Versions/A/QtGui', 'PySide6/Qt/lib'),
        ('/usr/local/opt/python@3.10/lib/python3.10/site-packages/PySide6/Qt/lib/QtWidgets.framework/Versions/A/QtWidgets', 'PySide6/Qt/lib'),
        ('/usr/local/opt/python@3.10/lib/python3.10/site-packages/PySide6/libpyside6.abi3.6.5.dylib', 'PySide6'),
        ('/usr/local/opt/python@3.10/lib/python3.10/site-packages/PySide6/libpyside6qml.abi3.6.5.dylib', 'PySide6')
    ],
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
