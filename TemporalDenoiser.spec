# TemporalDenoiser.spec
# PyInstaller spec file for macOS 13 runner with macOS 12 compatibility
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

def find_compatible_python_lib():
    """Find Python library with preference for compatibility"""
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    lib_name = f"libpython{python_version}.dylib"
    
    # Check pyenv installation first (most likely to be compatible)
    pyenv_root = os.environ.get('PYENV_ROOT', os.path.expanduser('~/.pyenv'))
    if os.path.exists(pyenv_root):
        pyenv_paths = [
            f"{pyenv_root}/versions/{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}/lib/{lib_name}",
            f"{pyenv_root}/versions/{python_version}/lib/{lib_name}"
        ]
        for path in pyenv_paths:
            if os.path.exists(path):
                print(f"Found pyenv Python library: {path}")
                return path
    
    # Check current Python installation
    possible_paths = [
        os.path.join(sys.prefix, 'lib', lib_name),
        os.path.join(sys.exec_prefix, 'lib', lib_name),
        f"/usr/local/lib/{lib_name}"
    ]
    
    # Add stdlib location
    try:
        stdlib_path = sysconfig.get_path('stdlib')
        lib_path = os.path.join(stdlib_path, '..', lib_name)
        lib_path = os.path.abspath(lib_path)
        possible_paths.insert(0, lib_path)
    except:
        pass
    
    # Check Homebrew paths last (might be less compatible)
    possible_paths.extend([
        f"/usr/local/opt/python@{python_version}/lib/{lib_name}",
        f"/usr/local/Cellar/python@{python_version}/*/lib/{lib_name}",
        f"/usr/local/opt/python@{python_version}/Frameworks/Python.framework/Versions/{python_version}/lib/{lib_name}"
    ])
    
    for path_pattern in possible_paths:
        if '*' in path_pattern:
            matches = glob.glob(path_pattern)
            if matches:
                path = matches[0]
            else:
                continue
        else:
            path = path_pattern
            
        if os.path.exists(path):
            print(f"Found Python library at: {path}")
            
            # Check if it's compatible (best effort)
            try:
                import subprocess
                result = subprocess.run(['otool', '-l', path], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # Look for version constraints
                    output = result.stdout.lower()
                    if 'minos 13.' in output or 'minos 14.' in output:
                        print(f"Warning: {path} may require macOS 13+, but will try to use it")
                    elif 'minos 12.' in output or 'minos 11.' in output or 'minos 10.' in output:
                        print(f"Good: {path} appears compatible with macOS 12")
                    else:
                        print(f"No explicit version constraint found in {path}")
            except Exception as e:
                print(f"Could not check compatibility of {path}: {e}")
            
            return path
    
    print(f"No Python library found. Searched: {possible_paths}")
    return None

def find_libraw():
    """Find libraw library"""
    possible_paths = [
        "/usr/local/lib/libraw.dylib",
        "/usr/local/opt/libraw/lib/libraw.dylib",
        "/usr/local/opt/libraw/lib/libraw.23.dylib",
        "/usr/local/opt/libraw/lib/libraw.20.dylib"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found libraw: {path}")
            return path
    
    # Search for any libraw version
    for pattern in ["/usr/local/opt/libraw/lib/libraw*.dylib", "/usr/local/lib/libraw*.dylib"]:
        matches = glob.glob(pattern)
        if matches:
            path = matches[0]
            print(f"Found libraw: {path}")
            return path
    
    print("libraw not found")
    return None

# Find libraries
python_lib = find_compatible_python_lib()
libraw_lib = find_libraw()

# Build binaries list
binaries = []

if python_lib:
    binaries.append((python_lib, '.'))
else:
    print("WARNING: No Python library found - app may not work")

if libraw_lib:
    binaries.append((libraw_lib, 'rawpy/libraw'))
else:
    print("WARNING: libraw not found - rawpy may not work")

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

# Collect package data files
packages_to_collect = ["PySide6", "rawpy", "cv2", "imageio", "numpy", "scipy", "tifffile"]
for pkg in packages_to_collect:
    pkg_data = safe_collect_data(pkg, include_py=False)
    data_files.extend(pkg_data)
    print(f"Collected {len(pkg_data)} data files for {pkg}")

# Collect PySide6 binaries specifically
try:
    pyside6_path = os.path.join(site_packages, "PySide6")
    if os.path.exists(pyside6_path):
        # Look for PySide6 dynamic libraries
        for pattern in ["libpyside6*.dylib", "libshiboken6*.dylib"]:
            for dylib in glob.glob(os.path.join(pyside6_path, pattern)):
                binaries.append((dylib, "PySide6"))
                print(f"Added PySide6 binary: {os.path.basename(dylib)}")
        
        # Look for Qt frameworks
        qt_lib_path = os.path.join(pyside6_path, "Qt", "lib")
        if os.path.exists(qt_lib_path):
            qt_frameworks = [
                "QtCore.framework/Versions/Current/QtCore",
                "QtGui.framework/Versions/Current/QtGui",
                "QtWidgets.framework/Versions/Current/QtWidgets"
            ]
            for framework in qt_frameworks:
                framework_path = os.path.join(qt_lib_path, framework)
                if os.path.exists(framework_path):
                    dest_path = f"PySide6/Qt/lib/{framework.split('/')[0]}"
                    binaries.append((framework_path, dest_path))
                    print(f"Added Qt framework: {framework.split('/')[0]}")
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
    
    # PySide6 core modules
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "shiboken6",
    
    # Image processing
    "imageio.plugins",
    "imageio.plugins._tifffile",
    
    # Scientific computing
    "numpy.core._multiarray_umath",
    "numpy.random._pickle",
    "scipy.sparse.csgraph._validation"
]

# Add package submodules
for pkg in ["PySide6", "cv2", "numpy", "scipy", "rawpy", "imageio"]:
    submodules = safe_collect_submodules(pkg)
    hidden_imports.extend(submodules)
    print(f"Added {len(submodules)} hidden imports for {pkg}")

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
    runtime_hooks=['runtime_hooks/pyi_rth_macos_compat.py'],  # Our compatibility hook
    excludes=[
        # Exclude heavy/unnecessary modules
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebChannel',
        'PySide6.QtQml',
        'PySide6.QtQuick',
        'PySide6.Qt3DCore',
        'PySide6.Qt3DRender',
        'tkinter',
        'matplotlib',
        'IPython',
        'jupyter',
        'notebook',
        'sphinx',
        'pytest'
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
        'LSMinimumSystemVersion': '12.0',  # Explicitly set minimum version
        'CFBundleName': 'TemporalDenoiser',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'LSApplicationCategoryType': 'public.app-category.photography',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'CFBundleExecutable': 'TemporalDenoiser'
    }
)
