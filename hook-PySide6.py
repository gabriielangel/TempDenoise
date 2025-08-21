# hooks/hook-PySide6.py
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all PySide6 submodules and data files
hiddenimports = collect_submodules("PySide6")
datas = collect_data_files("PySide6")