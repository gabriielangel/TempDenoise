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
    ],
    'includes': [
        'numpy',
        'scipy',
        'cv2',
        'rawpy',
        'imageio',
        'PySide6',
    ],
    'excludes': [
        'setuptools',
        'distutils',
        'pkg_resources',
        'wheel',
        'pip',
        'jaraco',  # prevents jaraco.context bloat error
    ],
    'compressed': True,
    'use_pkg_resources': False,  # 🚫 disable pkg_resources bootstrapping
    'plist': {
        'CFBundleName': 'TemporalDenoiser',
        'CFBundleShortVersionString': '1.0',
        'CFBundleVersion': '1.0',
    },
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
