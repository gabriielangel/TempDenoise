from setuptools import setup

APP = ['-m', 'temporal_denoiser']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['cv2', 'numpy', 'PySide6', 'imageio'],
    'plist': {
        'CFBundleName': 'TemporalDenoiser',
        'CFBundleIdentifier': 'com.example.temporaldenoiser',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
