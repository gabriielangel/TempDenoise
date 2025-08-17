# setup.py
import sys
import types

# Patch for Python 3.10: ensure importlib.resources is the backport
try:
    import importlib_resources as ilr
    # Create a fake "importlib" module if not present
    if "importlib" not in sys.modules:
        import importlib
    # Force submodule mapping
    sys.modules["importlib.resources"] = ilr
    # Also attach it as attribute of importlib
    import importlib as _importlib
    setattr(_importlib, "resources", ilr)
except ImportError:
    pass

from setuptools import setup

APP = ['temporal_denoiser/__main__.py']

OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'temporal_denoiser/resources/app_icon.icns',
    'packages': [
        'numpy',
        'scipy',
        'cv2',
        'rawpy',
        'imageio',
        'PySide6',
        'shiboken6',  # needed for PySide6
    ],
    'includes': [
        'numpy',
        'scipy',
        'cv2',
        'rawpy',
        'imageio',
        'PySide6',
        'shiboken6',
    ],
    'excludes': [
        'setuptools',
        'distutils',
        'pkg_resources',
        'wheel',
        'pip',
        'jaraco',
    ],
    'compressed': True,
    'plist': {
        'CFBundleName': 'TemporalDenoiser',
        'CFBundleShortVersionString': '1.0',
        'CFBundleVersion': '1.0',
        'LSMinimumSystemVersion': '12.0',  # force compatibility with macOS 12+
    },
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
)
