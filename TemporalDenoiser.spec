# TemporalDenoiser.spec
# PyInstaller spec file for macOS app bundle
# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os
import glob

# Project root directory
proj_root = Path(".").resolve()

# Dynamically locate rawpy/libraw
rawpy_path = "/usr/local/opt/python@3.10/lib/python3.10/site-packages/rawpy"
libraw_data = []
if os.path.exists(os.path.join(rawpy_path, "libraw")):
    libraw_data = [(os.path.join(rawpy_path, "libraw"), "rawpy/libraw")]

# Dynamically locate libraw dylib
libraw_binaries = []
libraw_path = "/usr/local/opt/libraw/lib"
if os.path.exists(libraw_path):
    libraw_files = glob.glob(os.path.join(libraw_path, "libraw*.dylib"))
    libraw_binaries = [(f, "rawpy/libraw") for f in libraw_files]

# Dynamically locate libpython3.10.dylib
python_lib_path = "/usr/local/opt/python@3.10/lib"
libpython_binaries = []
if os.path.exists(python_lib_path):
    libpython_files = glob.glob(os.path.join(python_lib_path, "libpython3.10.dylib"))
    if not libpython_files:
        libpython_files = glob.glob("/usr/local/Cellar/python@3.10/*/lib/libpython3.10.dylib")
    libpython_binaries = [(f, ".") for f in libpython_files]
else:
    libpython_binaries = [('/Users/runner/hostedtoolcache/Python/3.10.18/x64/lib/libpython3.10.dylib', '.')]

# Dynamically locate PySide6 libraries
pyside6_path = "/usr/local/opt/python@3.10/lib/python3.10/site-packages/PySide6"
pyside6_binaries = [
    (f"{pyside6_path}/libpyside6.abi3.6.5.dylib", "PySide6"),
    (f"{pyside6_path}/libpyside6qml.abi3.6.5.dylib", "PySide6")
]
# Include Qt/lib directory if it exists
qt_lib_path = f"{pyside6_path}/Qt/lib"
if os.path.exists(qt_lib_path):
    pyside6_binaries.append((f"{qt_lib_path}/*", "PySide6/Qt/lib"))

# Collect tifffile data files
tifffile_data = collect_data_files("tifffile", include_py_files=False)

# Hidden imports for all required modules
hidden_imports = (
    collect_submodules("PySide6")
    + collect_submodules("PySide6.scripts")
    + collect_submodules("cv2")
    + collect_submodules("scipy")
    + collect_submodules("numpy")
    + collect_submodules("rawpy")
    + collect_submodules("imageio")
    + collect_submodules("imageio.plugins")
    + collect_submodules("tifffile")
    + ["temporal_denoiser.cinemadng", "temporal_denoiser.denoise", "tifffile"]
)

block_cipher = None

a = Analysis(
    ['temporal_denoiser/__main__.py'],
    pathex=['/Users/runner/work/TempDenoise/TempDenoise'],
    binaries=libpython_binaries + libraw_binaries + pyside6_binaries,
    datas=[
        ('/usr/local/opt/python@3.10/lib/python3.10/site-packages/tifffile/*', 'tifffile'),
        ('/usr/local/opt/python@3.10/lib/python3.10/site-packages/PySide6/*', 'PySide6'),
        ('/usr/local/opt/python@3.10/lib/python3.10/site-packages/cv2/*', 'cv2'),
        ('/usr/local/opt/python@3.10/lib/python3.10/site-packages/rawpy/*', 'rawpy'),
        ('/usr/local/opt/python@3.10/lib/python3.10/site-packages/imageio/*', 'imageio'),
        ('temporal_denoiser/resources/app_icon.icns', '.')  # Correct icon path
    ] + libraw_data + tifffile_data,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    target_arch='x86_64',  # Ensure Intel compatibility
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
    bundle_identifier='com.gabriielangel.TemporalDenoiser',
    info_plist={
        'LSMinimumSystemVersion': '12.0'  # Ensure macOS 12 compatibility
    }
)
```

**Changes**:
- Removed specific Qt framework references (`QtCore`, `QtGui`, `QtWidgets`) to avoid path errors.
- Included `libpyside6.abi3.6.5.dylib` and `libpyside6qml.abi3.6.5.dylib` as primary `PySide6` binaries.
- Added dynamic inclusion of `PySide6/Qt/lib/*` if the directory exists.
- Added dynamic detection of `libpython3.10.dylib` from `/usr/local/opt/python@3.10/lib/` or `/usr/local/Cellar/python@3.10/*/lib/`, falling back to `/Users/runner/hostedtoolcache/Python/3.10.18/x64/lib/libpython3.10.dylib`.
- Retained dynamic `libraw*.dylib` detection, `rawpy/libraw`, `tifffile`, `target_arch='x86_64'`, and `info_plist`.

#### Step 3: Build and Test

1. **Commit Changes**:
   - Replace `main.yml` with artifact ID `f40ef0a6-0933-42a8-ab68-f095ded99634`, version ID `f5b6c7d8-4c3e-5f6a-8b7c-9d0e1f2a3b4c`.
   - Replace `TemporalDenoiser.spec` with artifact ID `491c9365-eb7e-4210-8ed1-f1a4f3e155a3`, version ID `e7f8a9b0-5c6d-7e8f-9a0b-1c2d3e4f5a6b`.
   - Verify `temporal_denoiser/resources/app_icon.icns` exists in `https://github.com/gabriielangel/TempDenoise`.
   - Commit and push to trigger a GitHub Actions build.

2. **Check Debug Output**:
   - Review the `Debug Homebrew Python and dependencies` log, especially:
     ```
     Searching for libpython3.10.dylib:
     find /usr/local/Cellar/python@3.10 -name "libpython3.10.dylib"
     Searching for libraw dylib:
     find /usr/local/opt/libraw/lib -name "libraw*.dylib"
     Searching for Qt frameworks in PySide6:
     find /usr/local/opt/python@3.10/lib/python3.10/site-packages/PySide6 -name "*.framework"
     Checking system Qt libraries:
     find /usr/local/lib -name "libQt*.dylib"
     ```
   - If `libpython3.10.dylib` is found (e.g., `/usr/local/Cellar/python@3.10/3.10.18/lib/libpython3.10.dylib`), confirm the `.spec` uses it.
   - If Qt frameworks are found (e.g., `/usr/local/opt/python@3.10/lib/python3.10/site-packages/PySide6/Qt/lib/QtCore.framework/Versions/5/QtCore`), update `pyside6_binaries`:
     ```python
     pyside6_binaries = [
         (f"{pyside6_path}/Qt/lib/QtCore.framework/Versions/5/QtCore", "PySide6/Qt/lib"),
         (f"{pyside6_path}/Qt/lib/QtGui.framework/Versions/5/QtGui", "PySide6/Qt/lib"),
         (f"{pyside6_path}/Qt/lib/QtWidgets.framework/Versions/5/QtWidgets", "PySide6/Qt/lib")
     ]
     ```
   - If `libraw*.dylib` is found (e.g., `libraw.23.dylib`), confirm the dynamic `glob` worked.

3. **Test the App**:
   - Download and mount the `TemporalDenoiser-dmg` artifact.
   - Move to `/Applications`:
     ```bash
     mv ~/Downloads/TemporalDenoiser.app /Applications
     ```
   - Remove the quarantine attribute:
     ```bash
     xattr -d com.apple.quarantine /Applications/TemporalDenoiser.app
     ```
   - Open the app:
     ```bash
     open /Applications/TemporalDenoiser.app
     ```
   - Allow in `System Preferences > Security & Privacy > General` > “Open Anyway” if prompted.
   - Verify the icon in Finder (`temporal_denoiser/resources/app_icon.icns`).
   - Check `libpython3.10.dylib` location:
     ```bash
     ls -l /Applications/TemporalDenoiser.app/Contents/Resources/libpython3.10.dylib
     ls -l /Applications/TemporalDenoiser.app/Contents/MacOS/libpython3.10.dylib
     ```
     If it’s in `Contents/MacOS/`, move it:
     ```bash
     mv /Applications/TemporalDenoiser.app/Contents/MacOS/libpython3.10.dylib /Applications/TemporalDenoiser.app/Contents/Resources/
     ```
   - Test functionality:
     - Load `.dng` files (e.g., `/Users/camilbelisle/M14-1908`).
     - Set output directory (e.g., `/Users/camilbelisle/denoised`).
     - Adjust parameters (`align=True`, `winsize=15`, `iterations=3`) and click “Denoise.”
     - Check for output files (`denoised_XXXXXX.png` or `.dng`) and terminal output:
       ```
       INFO:temporal_denoiser.main:Loaded 11 DNG files
       DEBUG:temporal_denoiser.cinemadng:Loaded 11 DNG files: [...]
       INFO:temporal_denoiser.main:Output directory set to /Users/camilbelisle/denoised
       DEBUG:temporal_denoiser.main:Starting denoising
       DEBUG:temporal_denoiser.cinemadng:Successfully read 11 images
       DEBUG:temporal_denoiser.cinemadng:Denoising frame 5 with frame_radius=3, spatial_median=0, align=True, winsize=15, iterations=3
       INFO:temporal_denoiser.cinemadng:Denoising completed
       INFO:temporal_denoiser.main:Denoised frame 5 displayed and saved to /Users/camilbelisle/denoised
       ```

#### Step 4: Fallback for `_mkfifoat` Error
If the app fails with:
```
Symbol not found: (_mkfifoat)
```
- **Manual `libpython3.10.dylib`**:
  - On your macOS 12.7 machine, download Python 3.10.8 from `https://www.python.org/ftp/python/3.10.8/Python-3.10.8-macos11.pkg`.
  - Extract `/Library/Frameworks/Python.framework/Versions/3.10/lib/libpython3.10.dylib`.
  - Upload it to `temporal_denoiser/resources/libpython3.10.dylib` in your repository.
  - Update `TemporalDenoiser.spec`:
    ```python
    libpython_binaries = [('temporal_denoiser/resources/libpython3.10.dylib', '.')]
    ```
- **Alternative Python Version**:
  - Modify `main.yml` to try `python@3.10.8`:
    ```yaml
    brew install gfortran python@3.10.8 libraw
    ```
  - Update `TemporalDenoiser.spec` paths to `/usr/local/opt/python@3.10.8`.

#### Step 5: Fallback if `PySide6` Fails
If the app fails with `ImportError: QtCore` or similar:
- Install `pyside6` locally on your macOS 12.7 machine:
  ```bash
  pip install pyside6
  ```
- Locate Qt frameworks (e.g., `/Users/<your-user>/Library/Python/3.10/lib/python/site-packages/PySide6/Qt/lib/`).
- Upload `QtCore.framework`, `QtGui.framework`, and `QtWidgets.framework` to `temporal_denoiser/resources/`.
- Update `TemporalDenoiser.spec`:
  ```python
  pyside6_binaries = [
      ('temporal_denoiser/resources/QtCore.framework/Versions/A/QtCore', 'PySide6/Qt/lib'),
      ('temporal_denoiser/resources/QtGui.framework/Versions/A/QtGui', 'PySide6/Qt/lib'),
      ('temporal_denoiser/resources/QtWidgets.framework/Versions/A/QtWidgets', 'PySide6/Qt/lib'),
      (f"{pyside6_path}/libpyside6.abi3.6.5.dylib", "PySide6"),
      (f"{pyside6_path}/libpyside6qml.abi3.6.5.dylib", "PySide6")
  ]
