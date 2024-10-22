from pathlib import Path
from typing import List
import numpy as np
from numpy.typing import NDArray
from PIL import Image

def save_tiff_stack(frames: List[NDArray[np.uint16]], file_path: Path):
    images = [Image.fromarray(frame) for frame in frames]
    images[0].save(file_path, save_all=True, append_images=images[1:], compression="tiff_deflate")
    print(f"Saved TIFF stack to {file_path}")