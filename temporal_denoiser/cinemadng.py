# CinemaDNG helpers (placeholders)
try:
    import rawpy
    HAS_RAWPY = True
except Exception:
    HAS_RAWPY = False

try:
    import tifffile
    HAS_TIFFFILE = True
except Exception:
    HAS_TIFFFILE = False

def available():
    return HAS_RAWPY and HAS_TIFFFILE
