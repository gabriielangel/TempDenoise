# TemporalDenoiser.spec
# PyInstaller spec file for macOS app bundle

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os

# Project root directory
proj_root = Path(".").resolve()

# Dynamically locate rawpy/libraw
rawpy_path = "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages/rawpy"
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
        ('/Users/runner/hostedtoolcache/Python/3.10.18/x64/lib/libpython3.10.dylib', '.'),
        ('/Users/runner/hostedtoolcache/Python/3.10.18/x64/lib/python3.10/site-packages/PySide6/Qt/lib/*.dylib', 'PySide6/Qt/lib')
    ],
    datas=[
        ('/Users/runner/hostedtoolcache/Python/3.10.18/x64/lib/python3.10/site-packages/tifffile/*', 'tifffile'),
        ('/Users/runner/hostedtoolcache/Python/3.10.18/x64/lib/python3.10/site-packages/PySide6/*', 'PySide6'),
        ('/Users/runner/hostedtoolcache/Python/3.10.18/x64/lib/python3.10/site-packages/cv2/*', 'cv2'),
        ('/Users/runner/hostedtoolcache/Python/3.10.18/x64/lib/python3.10/site-packages/rawpy/*', 'rawpy'),
        ('/Users/runner/hostedtoolcache/Python/3.10.18/x64/lib/python3.10/site-packages/imageio/*', 'imageio'),
        ('temporal_denoiser/resources/app_icon.icns', '.')  # Correct icon path
    ],
    hiddenimports=[
        'tifffile',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'cv2',
        'scipy',
        'numpy',
        'rawpy',
        'imageio'
    ],
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
    target_arch=None,
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
    bundle_identifier='com.gabriielangel.TemporalDenoiser'
)
