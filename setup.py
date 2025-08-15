# setup.py
from setuptools import setup

APP = ['temporal_denoiser/__main__.py']
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'temporal_denoiser/resources/app_icon.icns',
    'packages': ['numpy', 'scipy', 'opencv', 'rawpy', 'PySide6', 'imageio'],
    'plist': {
        'CFBundleName': 'TemporalDenoiser',
        'CFBundleShortVersionString': '1.0',
        'CFBundleVersion': '1.0',
    },
    'includes': ['numpy', 'scipy', 'opencv', 'rawpy', 'PySide6', 'imageio'],
    'excludes': [],
    'compressed': True,
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
