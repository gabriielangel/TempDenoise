# TemporalDenoiser.spec
# PyInstaller spec file for TemporalDenoiser

import os
import shutil
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

# ---- Fix for PySide6 Qt framework symlink conflicts ----
qt_frameworks = [
    "Qt3DAnimation.framework",
    "Qt3DCore.framework",
    "Qt3DRender.framework",
    "Qt3DInput.framework",
    "Qt3DLogic.framework",
    "Qt3DExtras.framework",
]

build_dir = Path("dist") / "TemporalDenoiser" / "_internal" / "PySide6" / "Qt" / "lib"
for fw in qt_frameworks:
    fw_path = build_dir / fw / "Resources"
    if fw_path.is_symlink():
        os.unlink(fw_path)
    elif fw_path.exists():
        shutil.rmtree(fw_path)

# ---- Normal PyInstaller spec begins ----
block_cipher = None

a = Analysis(
    ['temporal_denoiser/__main__.py'],
    pathex=[str(Path(__file__).parent)],
    binaries=[],
    datas=[
        ('temporal_denoiser/resources/app_icon.icns', '.'),
    ],
    hiddenimports=collect_submodules('PySide6'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['setuptools', 'distutils', 'pkg_resources', 'wheel', 'pip', 'jaraco'],
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
    name='TemporalDenoiser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='temporal_denoiser/resources/app_icon.icns',
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
