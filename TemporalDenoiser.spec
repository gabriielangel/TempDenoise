# TemporalDenoiser.spec
# PyInstaller spec file for macOS 12 compatibility using GitHub Actions setup-python
# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import glob
import sysconfig
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Ensure macOS 12 compatibility environment
os.environ['MACOSX_DEPLOYMENT_TARGET'] = '12.0'

# Project root directory
proj_root = Path(".").resolve()

# Get site-packages from current Python installation
site_packages = sysconfig.get_paths()['purelib']
print(f"Using site-packages: {site_packages}")

def find_python_lib():
    """Find Python library for the current installation"""
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    lib_name = f"libpython{python_version}.dylib"
    
    # Common locations for GitHub Actions setup-python
    possible_paths = [
        os.path.join(sys.prefix, 'lib', lib_name),
        os.path.join(sys.exec_prefix, 'lib', lib_name),
        f"/usr/local/lib/{lib_name}",
        f"/Library/Frameworks/Python.framework/Versions/{python_version}/lib/{lib_name}",
        f"/usr/local/opt/python@{python_version}/lib/{lib_name}"
    ]
    
    # Add stdlib location
    try:
        stdlib_path = sysconfig.get_path('stdlib')
        lib_path = os.path.join(stdlib_path, '..', lib_name)
        lib_path = os.path.abspath(lib_path)
        possible_paths.insert(0, lib_path)
    except:
        pass
    
    for path_pattern in possible_paths:
        if '*' in path_pattern:
            matches = glob.glob(path_pattern)
            path = matches[0] if matches else None
        else:
            path = path_pattern
            
        if path and os.path.exists(path):
            print(f"Found Python library at: {path}")
            return path
    
    print(f"No Python library found. Searched: {possible_paths}")
    return None

def find_libraw():
    """Find libraw library"""
    possible_paths = [
        "/usr/local/lib/libraw.dylib",
        "/usr/local/opt/libraw/lib/libraw.dylib",
        "/usr/local/opt/libraw/lib/libraw.23.dylib",
        "/usr/local/opt/libraw/lib/libraw.20.dylib",
        "/opt/homebrew/lib/libraw.dylib"  # Apple Silicon
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found libraw: {path}")
            return path
    
    # Search for any libraw version
    for pattern in ["/usr/local/opt/libraw/lib/libraw*.dylib", 
                   "/usr/local/lib/libraw*.dylib",
                   "/opt/homebrew/lib/libraw*.dylib"]:
        matches = glob.glob(pattern)
        if matches:
            path = matches[0]
            print(f"Found libraw: {path}")
            return path
    
    print("libraw not found - rawpy may not work properly")
    return None

# Find libraries
python_lib = find_python_lib()
libraw_lib = find_libraw()

# Build binaries list
binaries = []

if python_lib:
    binaries.append((python_lib, '.'))
else:
    print("WARNING: No Python library found - app may not work")

if libraw_lib:
    binaries.append((libraw_lib, '.'))

# Collect data files
data_files = [
    ('temporal_denoiser/resources/app_icon.icns', '.')
]

# Helper function to safely collect package data
def safe_collect_data(package_name, include_py=False):
    """Safely collect data files for a package"""
    try:
        return collect_data_files(package_name, include_py_files=include_py)
    except Exception as e:
        print(f"Could not collect {package_name} data: {e}")
        return []

def safe_collect_submodules(package_name):
    """Safely collect submodules for a package"""
    try:
        return collect_submodules(package_name)
    except Exception as e:
        print(f"Could not collect {package_name} submodules: {e}")
        return []

# Collect package data files (reduced list for reliability)
essential_packages = ["PySide6", "rawpy", "cv2", "imageio"]
for pkg in essential_packages:
    try:
        pkg_data = safe_collect_data(pkg, include_py=False)
        data_files.extend(pkg_data)
        print(f"Collected {len(pkg_data)} data files for {pkg}")
    except:
        print(f"Skipped data collection for {pkg}")

# Look for PySide6 Qt libraries specifically
try:
    pyside6_path = os.path.join(site_packages, "PySide6")
    if os.path.exists(pyside6_path):
        # Look for essential Qt libraries
        qt_lib_patterns = [
            os.path.join(pyside6_path, "*.dylib"),
            os.path.join(pyside6_path, "Qt", "lib", "*.dylib"),
            os.path.join(pyside6_path, "Qt", "lib", "Qt*.framework", "Versions", "Current", "Qt*")
        ]
        
        for pattern in qt_lib_patterns:
            for lib_file in glob.glob(pattern):
                if os.path.isfile(lib_file):
                    rel_path = os.path.relpath(lib_file, pyside6_path)
                    binaries.append((lib_file, f"PySide6/{os.path.dirname(rel_path)}" if os.path.dirname(rel_path) else "PySide6"))
                    print(f"Added PySide6 binary: {os.path.basename(lib_file)}")
                    
except Exception as e:
    print(f"Error collecting PySide6 binaries: {e}")

print(f"Total binaries: {len(binaries)}")
print(f"Total data files: {len(data_files)}")

# Collect hidden imports
hidden_imports = [
    # Core app modules
    "temporal_denoiser.cinemadng",
    "temporal_denoiser.denoise",
    
    # Essential packages
    "tifffile",
    "tifffile._tifffile",
    
    # PySide6 core modules
    "PySide6.QtCore",
    "PySide6.QtGui", 
    "PySide6.QtWidgets",
    "shiboken6",
    
    # Image processing essentials
    "imageio.plugins",
    "imageio.plugins.pillow",
    "imageio.plugins.tifffile",
    
    # Scientific computing
    "numpy.core._multiarray_umath",
    "numpy.random._pickle",
    
    # OpenCV essentials
    "cv2",
    "cv2.data"
]

# Add some submodules for critical packages
critical_packages = ["PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets"]
for pkg in critical_packages:
    try:
        submodules = safe_collect_submodules(pkg)
        hidden_imports.extend(submodules[:10])  # Limit to avoid bloat
    except:
        pass

print(f"Total hidden imports: {len(hidden_imports)}")

block_cipher = None

a = Analysis(
    ['temporal_denoiser/__main__.py'],
    pathex=[str(proj_root)],
    binaries=binaries,
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hooks/pyi_rth_macos_compat.py'],
    excludes=[
        # Exclude heavy/unnecessary modules
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets', 
        'PySide6.QtWebChannel',
        'PySide6.QtQml',
        'PySide6.QtQuick',
        'PySide6.Qt3DCore',
        'PySide6.Qt3DRender',
        'PySide6.QtMultimedia',
        'PySide6.QtCharts',
        'tkinter',
        'matplotlib',
        'IPython',
        'jupyter',
        'notebook',
        'sphinx',
        'pytest',
        'PyQt5',
        'PyQt6'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

# Filter out problematic files
def filter_binaries(binaries_list):
    """Filter out problematic or unnecessary binaries"""
    filtered = []
    skip_patterns = [
        'test_',
        '_test',
        '.pyo',
        'debug',
        'PyQt'
    ]
    
    for binary in binaries_list:
        name = binary[0] if isinstance(binary, tuple) else str(binary)
        if not any(pattern in name.lower() for pattern in skip_patterns):
            filtered.append(binary)
        else:
            print(f"Skipping binary: {name}")
    
    return filtered

a.binaries = filter_binaries(a.binaries)

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
    upx=False,  # Disable UPX to avoid compatibility issues
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
    upx=False,
    upx_exclude=[],
    name='TemporalDenoiser'
)

app = BUNDLE(
    coll,
    name='TemporalDenoiser.app',
    icon='temporal_denoiser/resources/app_icon.icns',
    bundle_identifier='com.gabrielangel.TemporalDenoiser',
    info_plist={
        'LSMinimumSystemVersion': '12.0',  # Explicitly set minimum version
        'CFBundleName': 'TemporalDenoiser',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'LSApplicationCategoryType': 'public.app-category.photography',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'CFBundleExecutable': 'TemporalDenoiser',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????'
    }
)
