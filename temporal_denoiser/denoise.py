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
            # Handle both file paths and numpy arrays
            processed_images = []
            for img in images:
                if isinstance(img, str):
                    # If it's a file path, read it
                    loaded_img = cv2.imread(img)
                    if loaded_img is None:
                        logger.error(f"Failed to load image from path: {img}")
                        return None, None
                    # Convert BGR to RGB for consistency
                    loaded_img = cv2.cvtColor(loaded_img, cv2.COLOR_BGR2RGB)
                    processed_images.append(loaded_img.astype(np.float32) / 255.0 if loaded_img.max() > 1.0 else loaded_img.astype(np.float32))
                else:
                    # If it's already a numpy array, use it directly
                    if img is None:
                        logger.error("Received None image in images list")
                        return None, None
                    # Ensure it's float32 and normalized
                    if img.max() > 1.0:
                        processed_images.append(img.astype(np.float32) / 255.0)
                    else:
                        processed_images.append(img.astype(np.float32))
            
            if not processed_images:
                logger.warning("No valid images provided for denoising")
                return None, None
            
            # Clamp frame_idx to valid range
            frame_idx = min(max(frame_idx, frame_radius), len(processed_images) - frame_radius - 1)
            orig = processed_images[frame_idx]
            
            if align and len(processed_images) > 1:
                aligned = []
                # Convert reference frame to grayscale for optical flow
                orig_gray = cv2.cvtColor((orig * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
                
                for i in range(max(0, frame_idx - frame_radius), min(len(processed_images), frame_idx + frame_radius + 1)):
                    if i != frame_idx:
                        # Convert current frame to grayscale for optical flow
                        curr_gray = cv2.cvtColor((processed_images[i] * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
                        
                        # Calculate optical flow
                        flow = cv2.calcOpticalFlowFarneback(
                            orig_gray, curr_gray,
                            None, 0.5, 3, winsize, iterations, 5, 1.2, 0
                        )
                        
                        # Create coordinate grids for remapping
                        h, w = flow.shape[:2]
                        flow = -flow
                        flow[:, :, 0] += np.arange(w)
                        flow[:, :, 1] += np.arange(h)[:, np.newaxis]
                        
                        # Apply alignment to the original float image
                        aligned_img = cv2.remap(processed_images[i], flow, None, cv2.INTER_LINEAR)
                        aligned.append(aligned_img)
                    else:
                        aligned.append(orig)
                processed_images = aligned
            else:
                # Use subset of images around target frame
                start_idx = max(0, frame_idx - frame_radius)
                end_idx = min(len(processed_images), frame_idx + frame_radius + 1)
                processed_images = processed_images[start_idx:end_idx]
            
            # Average the frames for denoising
            denoised = np.mean(processed_images, axis=0)
            
            # Apply spatial median filter if requested
            if spatial_median > 0:
                # Convert to uint8 for median filter, then back to float
                denoised_uint8 = (denoised * 255).astype(np.uint8)
                denoised_uint8 = cv2.medianBlur(denoised_uint8, spatial_median)
                denoised = denoised_uint8.astype(np.float32) / 255.0
            
            return orig, denoised
        except Exception as e:
            logger.error(f"Preview denoising failed: {e}")
            import traceback
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            raise

class StreamExporter:
    def export(self, images, output_dir, frame_radius, spatial_median, align=True, winsize=15, iterations=3):
        logger.debug(f"Exporting denoised images to {output_dir} with radius {frame_radius}, align={align}, winsize={winsize}, iterations={iterations}")
        try:
            # Handle both file paths and numpy arrays
            processed_images = []
            for img in images:
                if isinstance(img, str):
                    # If it's a file path, read it
                    loaded_img = cv2.imread(img)
                    if loaded_img is None:
                        logger.error(f"Failed to load image from path: {img}")
                        continue
                    # Convert BGR to RGB for consistency
                    loaded_img = cv2.cvtColor(loaded_img, cv2.COLOR_BGR2RGB)
                    processed_images.append(loaded_img.astype(np.float32) / 255.0 if loaded_img.max() > 1.0 else loaded_img.astype(np.float32))
                else:
                    # If it's already a numpy array, use it directly
                    if img is None:
                        logger.error("Received None image in images list")
                        continue
                    # Ensure it's float32 and normalized
                    if img.max() > 1.0:
                        processed_images.append(img.astype(np.float32) / 255.0)
                    else:
                        processed_images.append(img.astype(np.float32))
            
            if not processed_images:
                logger.warning("No valid images to export")
                return
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Process each frame
            for frame_idx in range(len(processed_images)):
                start_idx = max(0, frame_idx - frame_radius)
                end_idx = min(len(processed_images), frame_idx + frame_radius + 1)
                
                if align and end_idx - start_idx > 1:
                    aligned = []
                    orig = processed_images[frame_idx]
                    # Convert reference frame to grayscale for optical flow
                    orig_gray = cv2.cvtColor((orig * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
                    
                    for i in range(start_idx, end_idx):
                        if i != frame_idx:
                            # Convert current frame to grayscale for optical flow
                            curr_gray = cv2.cvtColor((processed_images[i] * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
                            
                            # Calculate optical flow
                            flow = cv2.calcOpticalFlowFarneback(
                                orig_gray, curr_gray,
                                None, 0.5, 3, winsize, iterations, 5, 1.2, 0
                            )
                            
                            # Create coordinate grids for remapping
                            h, w = flow.shape[:2]
                            flow = -flow
                            flow[:, :, 0] += np.arange(w)
                            flow[:, :, 1] += np.arange(h)[:, np.newaxis]
                            
                            # Apply alignment to the original float image
                            aligned_img = cv2.remap(processed_images[i], flow, None, cv2.INTER_LINEAR)
                            aligned.append(aligned_img)
                        else:
                            aligned.append(orig)
                    frame_images = aligned
                else:
                    frame_images = processed_images[start_idx:end_idx]
                
                # Average the frames for denoising
                denoised = np.mean(frame_images, axis=0)
                
                # Apply spatial median filter if requested
                if spatial_median > 0:
                    # Convert to uint8 for median filter, then back to float
                    denoised_uint8 = (denoised * 255).astype(np.uint8)
                    denoised_uint8 = cv2.medianBlur(denoised_uint8, spatial_median)
                    denoised = denoised_uint8.astype(np.float32) / 255.0
                
                # Save the denoised frame
                output_path = os.path.join(output_dir, f"denoised_{frame_idx:06d}.png")
                # Convert back to BGR for OpenCV saving
                denoised_bgr = cv2.cvtColor((denoised * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
                success = cv2.imwrite(output_path, denoised_bgr)
                
                if not success:
                    logger.error(f"Failed to write image: {output_path}")
                else:
                    logger.debug(f"Saved denoised frame {frame_idx} to {output_path}")
            
            logger.info(f"Exported {len(processed_images)} denoised images to {output_dir}")
        except Exception as e:
            logger.error(f"Export failed: {e}")
            import traceback
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            raise
