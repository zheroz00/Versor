"""
Potrace converter - outline tracing
Best for: solid shapes, silhouettes, CNC cutting
"""

import os
import subprocess
from config import POTRACE_PATH
from .dependencies import get_imagemagick_cmd


def convert_with_potrace(input_path, output_path, corner_threshold=0, optimize_tolerance=0.1,
                         despeckle=2, threshold=50, invert=False):
    """
    Convert a raster image to SVG using ImageMagick and Potrace.

    Produces outline paths that trace around the edges of shapes.

    Args:
        input_path: Path to input image
        output_path: Path for output SVG
        corner_threshold: Corner detection sensitivity (0=sharp, higher=rounded)
        optimize_tolerance: Curve optimization level
        despeckle: Noise removal threshold
        threshold: B/W conversion percentage
        invert: Whether to invert colors before tracing

    Returns:
        Tuple of (success: bool, message: str)
    """
    # Create temp BMP path
    bmp_path = input_path.rsplit('.', 1)[0] + '.bmp'

    try:
        # Build ImageMagick command for B/W conversion
        im_cmd = get_imagemagick_cmd()
        if not im_cmd:
            return False, "ImageMagick not found"

        magick_cmd = [im_cmd, input_path, "-threshold", f"{threshold}%"]
        if invert:
            magick_cmd.append("-negate")
        magick_cmd.append(bmp_path)

        # Convert to BMP
        result = subprocess.run(magick_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return False, f"ImageMagick error: {result.stderr}"

        # Run Potrace
        potrace_cmd = [
            POTRACE_PATH,
            bmp_path,
            "-s",  # SVG output
            "-a", str(corner_threshold),
            "-O", str(optimize_tolerance),
            "-t", str(despeckle),
            "-o", output_path
        ]

        result = subprocess.run(potrace_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return False, f"Potrace error: {result.stderr}"

        return True, "Success"

    finally:
        # Clean up temp BMP
        if os.path.exists(bmp_path):
            os.remove(bmp_path)
