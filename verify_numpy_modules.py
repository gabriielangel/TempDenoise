#!/usr/bin/env python3
"""
NumPy Module Verification Script
This script verifies that all critical NumPy modules are available
and can be imported successfully. Run this during the build process
to catch NumPy-related issues early.
"""

import sys
import os
import importlib.util

def test_module_import(module_name):
    """Test if a module can be imported successfully."""
    try:
        __import__(module_name)
        return True, "Success"
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {e}"

def test_module_spec(module_name):
    """Test if a module spec can be found."""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False, "No spec found"
        return True, spec.origin or "Built-in module"
    except Exception as e:
        return False, str(e)

def main():
    print("NumPy Module Verification Script")
    print("=" * 50)
    
    # Test basic NumPy import first
    try:
        import numpy
        print(f"NumPy version: {numpy.__version__}")
        print(f"NumPy location: {numpy.__file__}")
    except ImportError as e:
        print(f"CRITICAL: Cannot import NumPy at all: {e}")
        return 1
    
    # Critical modules that PyInstaller needs
    critical_modules = [
        # Core modules that commonly cause issues
        'numpy.core._multiarray_umath',
        'numpy.core._multiarray_tests',  # This is the main culprit
        'numpy.core.multiarray', 
        'numpy.core.umath',
        
        # Other important core modules
        'numpy.core._methods',
        'numpy.core._type_aliases',
        'numpy.core._dtype_ctypes',
        'numpy.core._internal',
        'numpy.core._exceptions',
        'numpy.core.numeric',
        'numpy.core.numerictypes',
        
        # Random modules
        'numpy.random.mtrand',
        'numpy.random._pickle',
        'numpy.random._common',
        'numpy.random._generator',
        
        # Linear algebra
        'numpy.linalg._umath_linalg',
        
        # FFT
        'numpy.fft._pocketfft_internal',
    ]
    
    print("\nTesting critical NumPy modules:")
    print("-" * 50)
    
    failed_imports = []
    failed_specs = []
    
    for module in critical_modules:
        # Test import
        import_success, import_msg = test_module_import(module)
        
        # Test spec discovery
        spec_success, spec_msg = test_module_spec(module)
        
        status = "✓" if import_success else "✗"
        print(f"{status} {module}")
        
        if import_success:
            print(f"    Import: SUCCESS")
        else:
            print(f"    Import: FAILED - {import_msg}")
            failed_imports.append(module)
            
        if spec_success:
            print(f"    Spec: Found at {spec_msg}")
        else:
            print(f"    Spec: FAILED - {spec_msg}")
            failed_specs.append(module)
        
        print()
    
    # Summary
    print("SUMMARY:")
    print("-" * 50)
    print(f"Total modules tested: {len(critical_modules)}")
    print(f"Import failures: {len(failed_imports)}")
    print(f"Spec failures: {len(failed_specs)}")
    
    if failed_imports:
        print(f"\nFailed imports (CRITICAL): {failed_imports}")
        
    if failed_specs:
        print(f"\nFailed specs (WARNING): {failed_specs}")
    
    # Test basic NumPy functionality
    print("\nTesting basic NumPy functionality:")
    try:
        import numpy as np
        arr = np.array([1, 2, 3])
        result = np.mean(arr)
        print(f"✓ Basic operations work: mean([1,2,3]) = {result}")
    except Exception as e:
        print(f"✗ Basic operations failed: {e}")
        failed_imports.append("basic_operations")
    
    # Test NumPy with other packages that commonly cause issues
    print("\nTesting NumPy compatibility with other packages:")
    test_packages = ['scipy', 'cv2', 'imageio']
    
    for pkg in test_packages:
        try:
            __import__(pkg)
            print(f"✓ {pkg} imports successfully with NumPy")
        except ImportError:
            print(f"- {pkg} not available (OK)")
        except Exception as e:
            print(f"✗ {pkg} failed to import: {e}")
    
    # Return appropriate exit code
    if failed_imports:
        print(f"\n❌ VERIFICATION FAILED: {len(failed_imports)} critical modules cannot be imported")
        return 1
    else:
        print(f"\n✅ VERIFICATION PASSED: All critical NumPy modules are available")
        return 0

if __name__ == "__main__":
    sys.exit(main())