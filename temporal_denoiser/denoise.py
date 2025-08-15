from typing import List, Tuple, Callable, Optional
import numpy as np, cv2
from pathlib import Path

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

def read_image(path: str) -> np.ndarray:
    p = Path(path)
    if p.suffix.lower() == '.dng' and HAS_RAWPY:
        with rawpy.imread(str(p)) as raw:
            rgb16 = raw.postprocess(output_bps=16, no_auto_bright=True, use_camera_wb=True)
        img = (rgb16.astype(np.float32)) / 65535.0
        return img
    img = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
    if img is None: raise IOError(f"Can't read image: {path}")
    if img.ndim == 2: img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.dtype == np.uint8: img = img.astype(np.float32) / 255.0
    elif img.dtype == np.uint16: img = img.astype(np.float32) / 65535.0
    else: img = img.astype(np.float32)
    return img[..., :3][:, :, ::-1]

def write_image(path: str, img: np.ndarray):
    p = Path(path)
    img16 = np.clip(img, 0, 1); img16 = (img16 * 65535.0).astype(np.uint16)
    if p.suffix.lower() == '.dng' and HAS_TIFFFILE:
        tifffile.imwrite(str(p), img16, photometric='rgb')
    else:
        out = (img.clip(0,1) * 255.0).astype(np.uint8)[..., ::-1]
        cv2.imwrite(str(p), out)

def rgb_to_gray_f32(img: np.ndarray) -> np.ndarray:
    g = cv2.cvtColor((img * 255.0).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    return g.astype(np.float32) / 255.0

def warp_to_center(src_rgb: np.ndarray, src_gray: np.ndarray, center_gray: np.ndarray,
                   winsize: int = 15, levels: int = 3, iterations: int = 3) -> np.ndarray:
    winsize = max(5, winsize | 1); levels = max(1, int(levels)); iterations = max(1, int(iterations))
    flow = cv2.calcOpticalFlowFarneback(src_gray, center_gray, None,
                                        pyr_scale=0.5, levels=levels, winsize=winsize,
                                        iterations=iterations, poly_n=5, poly_sigma=1.2, flags=0)
    h, w = src_gray.shape
    grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
    map_x = (grid_x + flow[..., 0]).astype(np.float32)
    map_y = (grid_y + flow[..., 1]).astype(np.float32)
    warped = cv2.remap((src_rgb * 255.0).astype(np.uint8), map_x, map_y,
                       interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return warped.astype(np.float32) / 255.0

class RollingBuffer:
    def __init__(self, paths: List[str]): self.paths=paths; self.n=len(paths); self.cache_rgb={}; self.cache_gray={}
    def get(self, idx: int):
        if idx in self.cache_rgb: return self.cache_rgb[idx], self.cache_gray[idx]
        rgb = read_image(self.paths[idx]); gray = rgb_to_gray_f32(rgb)
        self.cache_rgb[idx]=rgb; self.cache_gray[idx]=gray; return rgb, gray
    def ensure_window(self, start: int, end: int):
        for k in list(self.cache_rgb.keys()):
            if k<start or k>end:
                self.cache_rgb.pop(k, None); self.cache_gray.pop(k, None)
        for i in range(start, end+1):
            if i not in self.cache_rgb: self.get(i)

def aligned_average(buffer: RollingBuffer, center_idx: int, radius: int,
                    winsize: int, levels: int, iterations: int) -> np.ndarray:
        start = max(0, center_idx - radius); end = min(buffer.n - 1, center_idx + radius)
        center_rgb, center_gray = buffer.get(center_idx)
        aligned = [center_rgb]
        for j in range(start, end+1):
            if j == center_idx: continue
            src_rgb, src_gray = buffer.get(j)
            try:
                warped = warp_to_center(src_rgb, src_gray, center_gray, winsize, levels, iterations)
            except Exception:
                warped = src_rgb
            aligned.append(warped)
        return np.stack(aligned, axis=0).mean(axis=0)

def optional_spatial_median(img: np.ndarray, k: int) -> np.ndarray:
    if not k or k<=1: return img
    tmp = (img.clip(0,1) * 255.0).astype(np.uint8)
    tmp = cv2.medianBlur(tmp, k)
    return tmp.astype(np.float32) / 255.0

class PreviewDenoiser:
    def preview(self, paths: List[str], idx: int, frame_radius: int, spatial_median: int,
                winsize: int = 15, levels: int = 3, iterations: int = 3):
        if not paths: raise ValueError('No paths provided')
        idx = max(0, min(idx, len(paths)-1))
        buf = RollingBuffer(paths)
        start = max(0, idx - frame_radius); end = min(len(paths)-1, idx + frame_radius)
        buf.ensure_window(start, end)
        deno = aligned_average(buf, idx, frame_radius, winsize, levels, iterations)
        deno = optional_spatial_median(deno, spatial_median if spatial_median and spatial_median>1 else 0)
        orig, _ = buf.get(idx); return orig, deno

class StreamExporter:
    def export(self, paths: List[str], out_dir: str, frame_radius: int, spatial_median: int,
               progress_cb: Optional[Callable[[int, int], None]] = None,
               winsize: int = 15, levels: int = 3, iterations: int = 3):
        n = len(paths); 
        if n == 0: return
        out_dir_p = Path(out_dir); out_dir_p.mkdir(parents=True, exist_ok=True)
        buf = RollingBuffer(paths)
        for i in range(n):
            start = max(0, i - frame_radius); end = min(n-1, i + frame_radius)
            buf.ensure_window(start, end)
            out = aligned_average(buf, i, frame_radius, winsize, levels, iterations)
            out = optional_spatial_median(out, spatial_median if spatial_median and spatial_median>1 else 0)
            name = Path(paths[i]).stem; ext = Path(paths[i]).suffix or '.png'
            if ext.lower()=='.dng' and not HAS_TIFFFILE: ext = '.png'
            outname = f"{name}_denoised{ext}"
            write_image(str(out_dir_p / outname), out)
            if progress_cb: progress_cb(i+1, n)
