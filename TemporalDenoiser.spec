# TemporalDenoiser.spec
# PyInstaller spec file for macOS app bundle

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

# Project root directory
proj_root = Path(".").resolve()

# Hidden imports for PySide6 and other libs
hidden_imports = (
    collect_submodules("PySide6")
    + collect_submodules("cv2")
    + collect_submodules("scipy")
    + collect_submodules("numpy")
)

block_cipher = None

a = Analysis(
    [str(proj_root / "temporal_denoiser/__main__.py")],
    pathex=[str(proj_root)],
    binaries=[
        # Explicitly exclude libpython3.10.dylib to ensure framework Python is used
        (None, "libpython3.10.dylib"),
    ],
    datas=[
        (str(proj_root / "temporal_denoiser/resources/app_icon.icns"), "resources"),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["distutils", "setuptools", "pkg_resources", "wheel", "pip", "jaraco", "libpython3.10.dylib"],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    icon=str(proj_root / "temporal_denoiser/resources/app_icon.icns"),
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
    icon=str(proj_root / "temporal_denoiser/resources/app_icon.icns"),
    bundle_identifier="com.temporaldenoiser.app",
    info_plist={
        "CFBundleName": "TemporalDenoiser",
        "CFBundleShortVersionString": "1.0",
        "CFBundleVersion": "1.0",
        "NSHighResolutionCapable": "True",
        "LSMinimumSystemVersion": "12.0",  # Ensure macOS 12 compatibility
    },
    # Use system Python runtime to avoid embedding incompatible libpython
    runtime_tmpdir=None,
)
