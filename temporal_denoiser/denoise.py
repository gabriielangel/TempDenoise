import numpy as np
import cv2
import os  # Added missing import
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PreviewDenoiser:
    def preview(self, images, frame_idx, frame_radius, spatial_median, align=True, winsize=15, iterations=3):
        logger.debug(f"Preview denoising frame {frame_idx} with radius {frame_radius}, align={align}, winsize={winsize}, iterations={iterations}")
        try:
            images = [cv2.imread(img) if isinstance(img, str) else img for img in images]
            images = [img.astype(np.float32) / 255.0 if img.max() > 1.0 else img for img in images]
            if not images:
                logger.warning("No images provided for denoising")
                return None, None
            frame_idx = min(max(frame_idx, frame_radius), len(images) - frame_radius - 1)
            orig = images[frame_idx]
            if align and len(images) > 1:
                aligned = []
                for i in range(max(0, frame_idx - frame_radius), min(len(images), frame_idx + frame_radius + 1)):
                    if i != frame_idx:
                        flow = cv2.calcOpticalFlowFarneback(
                            cv2.cvtColor(orig, cv2.COLOR_RGB2GRAY),
                            cv2.cvtColor(images[i], cv2.COLOR_RGB2GRAY),
                            None, 0.5, 3, winsize, iterations, 5, 1.2, 0
                        )
                        h, w = flow.shape[:2]
                        flow = -flow
                        flow[:, :, 0] += np.arange(w)
                        flow[:, :, 1] += np.arange(h)[:, np.newaxis]
                        aligned.append(cv2.remap(images[i], flow, None, cv2.INTER_LINEAR))
                    else:
                        aligned.append(orig)
                images = aligned
            else:
                images = images[max(0, frame_idx - frame_radius):frame_idx + frame_radius + 1]
            denoised = np.mean(images, axis=0)
            if spatial_median > 0:
                denoised = cv2.medianBlur(denoised, spatial_median)
            return orig, denoised
        except Exception as e:
            logger.error(f"Preview denoising failed: {e}")
            raise

class StreamExporter:
    def export(self, images, output_dir, frame_radius, spatial_median, align=True, winsize=15, iterations=3):
        logger.debug(f"Exporting denoised images to {output_dir} with radius {frame_radius}, align={align}, winsize={winsize}, iterations={iterations}")
        try:
            images = [cv2.imread(img) if isinstance(img, str) else img for img in images]
            images = [img.astype(np.float32) / 255.0 if img.max() > 1.0 else img for img in images]
            os.makedirs(output_dir, exist_ok=True)
            for frame_idx in range(len(images)):
                start_idx = max(0, frame_idx - frame_radius)
                end_idx = min(len(images), frame_idx + frame_radius + 1)
                if align and end_idx - start_idx > 1:
                    aligned = []
                    orig = images[frame_idx]
                    for i in range(start_idx, end_idx):
                        if i != frame_idx:
                            flow = cv2.calcOpticalFlowFarneback(
                                cv2.cvtColor(orig, cv2.COLOR_RGB2GRAY),
                                cv2.cvtColor(images[i], cv2.COLOR_RGB2GRAY),
                                None, 0.5, 3, winsize, iterations, 5, 1.2, 0
                            )
                            h, w = flow.shape[:2]
                            flow = -flow
                            flow[:, :, 0] += np.arange(w)
                            flow[:, :, 1] += np.arange(h)[:, np.newaxis]
                            aligned.append(cv2.remap(images[i], flow, None, cv2.INTER_LINEAR))
                        else:
                            aligned.append(orig)
                    frame_images = aligned
                else:
                    frame_images = images[start_idx:end_idx]
                denoised = np.mean(frame_images, axis=0)
                if spatial_median > 0:
                    denoised = cv2.medianBlur(denoised, spatial_median)
                output_path = os.path.join(output_dir, f"denoised_{frame_idx:06d}.png")
                cv2.imwrite(output_path, (denoised * 255).astype(np.uint8))
            logger.info(f"Exported {len(images)} denoised images to {output_dir}")
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise
