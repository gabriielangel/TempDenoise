# hooks/hook-numpy.py
# PyInstaller hook for comprehensive NumPy support
# This ensures all required NumPy modules are included, especially test modules

from PyInstaller.utils.hooks import collect_submodules, collect_data_files, is_module_satisfies
import os

# Collect all NumPy submodules
hiddenimports = collect_submodules('numpy')

# Add specific modules that are commonly missing
critical_modules = [
    'numpy.core._multiarray_tests',  # This is the key missing module!
    'numpy.core._multiarray_umath',
    'numpy.core.multiarray',
    'numpy.core.umath',
    'numpy.core._methods',
    'numpy.core._type_aliases',
    'numpy.core._dtype_ctypes',
    'numpy.core._internal',
    'numpy.core._exceptions',
    'numpy.core._string_helpers',
    'numpy.core._ufunc_config',
    'numpy.core.arrayprint',
    'numpy.core.defchararray',
    'numpy.core.einsumfunc',
    'numpy.core.fromnumeric',
    'numpy.core.function_base',
    'numpy.core.getlimits',
    'numpy.core.machar',
    'numpy.core.memmap',
    'numpy.core.numeric',
    'numpy.core.numerictypes',
    'numpy.core.overrides',
    'numpy.core.records',
    'numpy.core.shape_base',
    'numpy.random._pickle',
    'numpy.random.mtrand',
    'numpy.random._common',
    'numpy.random._generator',
    'numpy.random._mt19937',
    'numpy.random._philox',
    'numpy.random._pcg64',
    'numpy.random._sfc64',
    'numpy.random.bit_generator',
]

# Add critical modules to hidden imports if not already present
for module in critical_modules:
    if module not in hiddenimports:
        hiddenimports.append(module)

# Collect data files
datas = collect_data_files('numpy', include_py_files=False)

# Also collect binary files (.so, .dylib, .pyd)
try:
    import numpy
    numpy_dir = os.path.dirname(numpy.__file__)
    
    binaries = []
    
    # Look for all binary extensions in numpy directory
    import glob
    for pattern in ['**/*.so', '**/*.dylib', '**/*.pyd']:
        for binary_file in glob.glob(os.path.join(numpy_dir, pattern), recursive=True):
            if os.path.isfile(binary_file):
                # Calculate relative path from numpy root
                rel_path = os.path.relpath(binary_file, numpy_dir)
                dest_dir = os.path.dirname(rel_path)
                if dest_dir:
                    dest_path = f'numpy/{dest_dir}'
                else:
                    dest_path = 'numpy'
                binaries.append((binary_file, dest_path))
    
    # Export binaries for PyInstaller
    if binaries:
        globals()['binaries'] = binaries
        
except ImportError:
    pass

print(f"NumPy hook: collected {len(hiddenimports)} hidden imports and {len(datas)} data files")