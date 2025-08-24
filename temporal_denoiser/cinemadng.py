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
except Exception as e:
    HAS_RAWPY = False
    logger.warning(f"rawpy import failed: {e}; CinemaDNG file processing will be disabled")

try:
    import tifffile
    HAS_TIFFFILE = True
except Exception as e:
    HAS_TIFFFILE = False
    logger.warning(f"tifffile import failed: {e}; DNG output will use fallback (PNG)")
    logger.debug("tifffile import failure details:", exc_info=True)

def available():
    return HAS_RAWPY and HAS_TIFFFILE

try:
    class CinemaDNG:
        def __init__(self, file_path):
            logger.debug(f"Initializing CinemaDNG with file_path: {file_path}")
            self.images = []
            try:
                if not HAS_RAWPY:
                    logger.warning("Cannot load CinemaDNG files without rawpy")
                    return
                # Handle single file, multiple files, or directory
                if isinstance(file_path, (list, tuple)):
                    self.images = [str(Path(f)) for f in file_path]
                elif Path(file_path).is_dir():
                    self.images = [str(f) for f in Path(file_path).glob("*.dng")]
                else:
                    self.images = [str(Path(file_path))]
                logger.debug(f"Loaded {len(self.images)} DNG files: {self.images}")
            except Exception as e:
                logger.error(f"Failed to load CinemaDNG files: {e}")
                raise

        def get_images(self):
            logger.debug("Returning images from CinemaDNG")
            try:
                if not HAS_RAWPY:
                    logger.warning("Cannot read images without rawpy")
                    return []
                # Read images using rawpy
                images = []
                for path in self.images:
                    try:
                        img = rawpy.imread(path).postprocess(output_bps=16, no_auto_bright=True, use_camera_wb=True)
                        images.append(img.astype(np.float32) / 65535.0)
                    except Exception as e:
                        logger.error(f"Failed to read image {path}: {e}")
                logger.debug(f"Successfully read {len(images)} images")
                return images
            except Exception as e:
                logger.error(f"Failed to read images: {e}")
                raise

        def denoise(self, frame_idx: int, frame_radius: int = 3, spatial_median: int = 0, align: bool = True, winsize: int = 15, iterations: int = 3):
            logger.debug(f"Denoising frame {frame_idx} with frame_radius={frame_radius}, spatial_median={spatial_median}, align={align}, winsize={winsize}, iterations={iterations}")
            try:
                if not self.images:
                    logger.warning("No images loaded for denoising")
                    return None
                denoiser = PreviewDenoiser()
                orig, denoised = denoiser.preview(self.images, frame_idx, frame_radius, spatial_median, align=align, winsize=winsize, iterations=iterations)
                logger.info("Denoising completed")
                return denoised
            except Exception as e:
                logger.error(f"Denoising failed: {e}")
                raise

        def save_denoised(self, output_dir, frame_radius=3, spatial_median=0, align=True, winsize=15, iterations=3):
            logger.debug(f"Saving denoised images to {output_dir}")
            try:
                if not self.images:
                    logger.warning("No images loaded for saving")
                    return
                os.makedirs(output_dir, exist_ok=True)
                exporter = StreamExporter()
                exporter.export(self.images, output_dir, frame_radius, spatial_median, align=align, winsize=winsize, iterations=iterations)
                if not HAS_TIFFFILE:
                    logger.warning("Saved images as PNG due to missing tifffile")
                else:
                    logger.info("Saved images as DNG")
                logger.info(f"Denoised images saved to {output_dir}")
            except Exception as e:
                logger.error(f"Failed to save denoised images: {e}")
                raise

except Exception as e:
    logger.error(f"Failed to define CinemaDNG class: {e}")
    raise
