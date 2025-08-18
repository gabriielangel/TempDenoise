# TemporalDenoiser.spec

# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

proj_root = Path.cwd()

# Collect all PySide6 hidden imports
pyside6_hidden = collect_submodules('PySide6')

a = Analysis(
    ['temporal_denoiser/__main__.py'],
    pathex=[str(proj_root)],
    binaries=[],
    datas=[
        ('temporal_denoiser/resources/app_icon.icns', '.'),  # include app icon
    ],
    hiddenimports=[
        'numpy',
        'scipy',
        'cv2',
        'rawpy',
        'imageio',
        *pyside6_hidden,   # all PySide6 plugins and backends
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'setuptools',
        'distutils',
        'pkg_resources',
        'wheel',
        'pip',
        'jaraco',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

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
    console=False,  # GUI app
    icon='temporal_denoiser/resources/app_icon.icns',
)

app = BUNDLE(
    exe,
    name='TemporalDenoiser.app',
    icon='temporal_denoiser/resources/app_icon.icns',
    bundle_identifier='com.example.temporaldenoiser',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TemporalDenoiser',
)
