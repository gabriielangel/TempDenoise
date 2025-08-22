import numpy as np
import imageio
import rawpy
import os
from temporal_denoiser.denoise import PreviewDenoiser, StreamExporter
import logging
from pathlib import Path

# Set up logging to debug initialization issues
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    import rawpy
    HAS_RAWPY = True
except Exception:
    HAS_RAWPY = False
    logger.error("rawpy import failed")

try:
    import tifffile
    HAS_TIFFFILE = True
except Exception:
    HAS_TIFFFILE = False
    logger.error("tifffile import failed")

def available():
    return HAS_RAWPY and HAS_TIFFFILE

try:
    class CinemaDNG:
        def __init__(self, file_path):
            logger.debug(f"Initializing CinemaDNG with file_path: {file_path}")
            self.file_path = Path(file_path)
            self.images = []
            try:
                if not HAS_RAWPY:
                    raise ImportError("rawpy is required to load CinemaDNG files")
                # Load DNG files from a directory or single file
                if self.file_path.is_dir():
                    self.images = [str(f) for f in self.file_path.glob("*.dng")]
                else:
                    self.images = [str(self.file_path)]
                logger.debug(f"Loaded {len(self.images)} DNG files: {self.images}")
            except Exception as e:
                logger.error(f"Failed to load CinemaDNG files: {e}")
                raise

        def get_images(self):
            logger.debug("Returning images from CinemaDNG")
            try:
                # Read images using rawpy
                return [rawpy.imread(path).postprocess(output_bps=16, no_auto_bright=True, use_camera_wb=True).astype(np.float32) / 65535.0 for path in self.images]
            except Exception as e:
                logger.error(f"Failed to read images: {e}")
                raise

        def denoise(self, frame_radius: int = 3, spatial_median: int = 0):
            logger.debug(f"Denoising with frame_radius={frame_radius}, spatial_median={spatial_median}")
            try:
                denoiser = PreviewDenoiser()
                idx = len(self.images) // 2  # Process middle frame as example
                orig, denoised = denoiser.preview(self.images, idx, frame_radius, spatial_median)
                return denoised
            except Exception as e:
                logger.error(f"Denoising failed: {e}")
                raise

except Exception as e:
    logger.error(f"Failed to define CinemaDNG class: {e}")
    raise
