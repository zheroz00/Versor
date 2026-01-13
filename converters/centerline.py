"""
Centerline converter - single-line tracing using autotrace
Best for: line art, text, engraving, technical drawings
"""

import os
import subprocess
from config import AUTOTRACE_PATH
from .dependencies import get_imagemagick_cmd

# Autotrace supported output formats
AUTOTRACE_FORMATS = ['svg', 'dxf', 'eps', 'pdf']


def convert_with_centerline(input_path, output_path, despeckle_level=2,
                            corner_threshold=100, line_threshold=1.0,
                            threshold=50, invert=False, output_format='svg'):
    """
    Convert a raster image to SVG/DXF/EPS/PDF using autotrace with centerline mode.

    Produces single-line paths through the middle of strokes instead of outlines.
    Ideal for engraving where you want one pass instead of two.

    Args:
        input_path: Path to input image
        output_path: Path for output file
        despeckle_level: Noise removal (0-20, higher = more removal)
        corner_threshold: Corner detection angle in degrees (0-180)
        line_threshold: Minimum line length to keep
        threshold: B/W conversion percentage
        invert: Whether to invert colors before tracing
        output_format: Output format: 'svg', 'dxf', 'eps', or 'pdf'

    Returns:
        Tuple of (success: bool, message: str)
    """
    # Create temp PBM path (autotrace prefers PBM/PGM)
    pbm_path = input_path.rsplit('.', 1)[0] + '.pbm'

    # Validate format
    fmt = output_format.lower() if output_format in AUTOTRACE_FORMATS else 'svg'

    try:
        # Preprocess with ImageMagick (convert to PBM)
        im_cmd = get_imagemagick_cmd()
        if not im_cmd:
            return False, "ImageMagick not found"

        magick_cmd = [im_cmd, input_path, "-threshold", f"{threshold}%"]
        if invert:
            magick_cmd.append("-negate")
        magick_cmd.append(pbm_path)

        result = subprocess.run(magick_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return False, f"ImageMagick error: {result.stderr}"

        # Run autotrace with centerline flag
        autotrace_cmd = [
            AUTOTRACE_PATH,
            "-centerline",
            "-output-format", fmt,
            "-despeckle-level", str(despeckle_level),
            "-corner-threshold", str(corner_threshold),
            "-line-threshold", str(line_threshold),
            "-output-file", output_path,
            pbm_path
        ]

        result = subprocess.run(autotrace_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return False, f"Autotrace error: {result.stderr}"

        return True, "Success"

    finally:
        # Clean up temp PBM
        if os.path.exists(pbm_path):
            os.remove(pbm_path)
