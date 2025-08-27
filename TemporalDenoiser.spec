# TemporalDenoiser.spec
# PyInstaller spec file for macOS app bundle
# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os
import glob
import sys

# Project root directory
proj_root = Path(".").resolve()

# Base site-packages path
site_packages = "/usr/local/opt/python@3.10/lib/python3.10/site-packages"

# Function to find Python library dynamically
def find_python_lib():
    """Find libpython3.10.dylib dynamically"""
    possible_paths = [
        "/usr/local/opt/python@3.10/lib/libpython3.10.dylib",
        "/usr/local/Cellar/python@3.10/3.10.18/lib/libpython3.10.dylib",
        "/usr/local/lib/libpython3.10.dylib",
        f"{sys.prefix}/lib/libpython3.10.dylib"
    ]
    
    # Also check in Frameworks
    framework_paths = [
        "/usr/local/opt/python@3.10/Frameworks/Python.framework/Versions/3.10/lib/libpython3.10.dylib",
        "/usr/local/Cellar/python@3.10/3.10.18/Frameworks/Python.framework/Versions/3.10/lib/libpython3.10.dylib"
    ]
    possible_paths.extend(framework_paths)
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found Python library at: {path}")
            return path
    
    print(f"Python library not found. Checked paths: {possible_paths}")
    return None

# Function to find libraw dynamically
def find_libraw():
    """Find libraw dylib dynamically"""
    possible_paths = [
        "/usr/local/opt/libraw/lib/libraw.23.dylib",
        "/usr/local/lib/libraw.23.dylib",
        "/usr/local/opt/libraw/lib/libraw.dylib"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found libraw at: {path}")
            return path
    
    # Try to find any libraw version
    for pattern in ["/usr/local/opt/libraw/lib/libraw*.dylib", "/usr/local/lib/libraw*.dylib"]:
        matches = glob.glob(pattern)
        if matches:
            print(f"Found libraw at: {matches[0]}")
            return matches[0]
    
    print(f"libraw not found. Checked paths: {possible_paths}")
    return None

# Dynamically locate libraries
python_lib = find_python_lib()
libraw_path = find_libraw()

# Build binaries list
libpython_binaries = [(python_lib, '.')] if python_lib else []
libraw_binaries = [(libraw_path, 'rawpy/libraw')] if libraw_path else []

# Dynamically locate rawpy/libraw data
rawpy_path = f"{site_packages}/rawpy"
libraw_data = []
if os.path.exists(os.path.join(rawpy_path, "libraw")):
    libraw_data = [(os.path.join(rawpy_path, "libraw"), "rawpy/libraw")]

# Dynamically locate PySide6 libraries
pyside6_path = f"{site_packages}/PySide6"
pyside6_binaries = []
pyside6_data = []
if os.path.exists(pyside6_path):
    # Look for PySide6 dylibs
    for pattern in ["libpyside6*.dylib", "libpyside6qml*.dylib", "libshiboken6*.dylib"]:
        for dylib in glob.glob(f"{pyside6_path}/{pattern}"):
            pyside6_binaries.append((dylib, "PySide6"))
    
    # Include PySide6 data files
    pyside6_data = collect_data_files("PySide6", include_py_files=False)
    
    # Look for Qt frameworks
    qt_lib_path = f"{pyside6_path}/Qt/lib"
    if os.path.exists(qt_lib_path):
        qt_frameworks = [
            'QtCore.framework/Versions/Current/QtCore',
            'QtGui.framework/Versions/Current/QtGui', 
            'QtWidgets.framework/Versions/Current/QtWidgets',
            'QtOpenGL.framework/Versions/Current/QtOpenGL'
        ]
        for framework in qt_frameworks:
            framework_path = f"{qt_lib_path}/{framework}"
            if os.path.exists(framework_path):
                pyside6_binaries.append((framework_path, f"PySide6/Qt/lib/{framework.split('/')[0]}"))

print(f"Found {len(pyside6_binaries)} PySide6 binaries")
print(f"Found {len(pyside6_data)} PySide6 data files")

# Collect data for other packages
data_files = []

# Add tifffile data if available
try:
    tifffile_data = collect_data_files("tifffile", include_py_files=False)
    data_files.extend(tifffile_data)
except Exception as e:
    print(f"Could not collect tifffile data: {e}")

# Add other package data
for pkg, pkg_name in [("rawpy", "rawpy"), ("cv2", "cv2"), ("imageio", "imageio"), 
                      ("numpy", "numpy"), ("scipy", "scipy")]:
    pkg_path = f"{site_packages}/{pkg}"
    if os.path.exists(pkg_path):
        try:
            pkg_data = collect_data_files(pkg, include_py_files=False)
            data_files.extend(pkg_data)
        except Exception as e:
            print(f"Could not collect {pkg} data: {e}")

# Hidden imports for all required modules
hidden_imports = [
    "temporal_denoiser.cinemadng", 
    "temporal_denoiser.denoise",
    "tifffile"
]

# Add PySide6 imports
try:
    pyside6_imports = collect_submodules("PySide6")
    hidden_imports.extend(pyside6_imports)
except Exception as e:
    print(f"Could not collect PySide6 submodules: {e}")

# Add other package imports
for pkg in ["cv2", "scipy", "numpy", "rawpy", "imageio"]:
    try:
        pkg_imports = collect_submodules(pkg)
        hidden_imports.extend(pkg_imports)
    except Exception as e:
        print(f"Could not collect {pkg} submodules: {e}")

# Add specific imageio plugins
hidden_imports.extend([
    "imageio.plugins",
    "imageio.plugins._tifffile"
])

print(f"Total hidden imports: {len(hidden_imports)}")

block_cipher = None

a = Analysis(
    ['temporal_denoiser/__main__.py'],
    pathex=[str(proj_root)],
    binaries=libpython_binaries + libraw_binaries + pyside6_binaries,
    datas=[
        ('temporal_denoiser/resources/app_icon.icns', '.')
    ] + libraw_data + pyside6_data + data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets', 
        'PySide6.QtWebChannel',
        'PySide6.QtQml',
        'PySide6.QtQuick',
        'tkinter',
        'matplotlib',
        'IPython'
    ],
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
    target_arch='x86_64',
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
    bundle_identifier='com.gabrielangel.TemporalDenoiser',
    info_plist={
        'LSMinimumSystemVersion': '12.0',
        'CFBundleName': 'TemporalDenoiser',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0'
    }
)
