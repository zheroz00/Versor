"""
vtracer converter - color/detail tracing
Best for: detailed artwork, illustrations, pixel art, color images
"""

import subprocess
from config import VTRACER_PATH


def convert_with_vtracer(input_path, output_path, mode="spline",
                         color_precision=6, gradient_step=8,
                         corner_threshold=60, segment_length=4,
                         splice_threshold=45, filter_speckle=4):
    """
    Convert a raster image to SVG using vtracer.

    Preserves colors and fine details. Can produce either sharp polygon
    paths or smooth spline curves.

    Args:
        input_path: Path to input image
        output_path: Path for output SVG
        mode: 'pixel', 'polygon', or 'spline' for different curve fitting
        color_precision: Number of significant bits in RGB channel (1-8)
        gradient_step: Color difference between gradient layers
        corner_threshold: Minimum angle (degrees) to be considered a corner
        segment_length: Max segment length before subdivision
        splice_threshold: Minimum angle displacement to splice a spline
        filter_speckle: Discard patches smaller than this size in pixels

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # vtracer handles the image directly - no preprocessing needed
        vtracer_cmd = [
            VTRACER_PATH,
            "--input", input_path,
            "--output", output_path,
            "--mode", mode,
            "--colormode", "color",
            "--color_precision", str(color_precision),
            "--gradient_step", str(gradient_step),
            "--corner_threshold", str(corner_threshold),
            "--segment_length", str(segment_length),
            "--splice_threshold", str(splice_threshold),
            "--filter_speckle", str(filter_speckle)
        ]

        result = subprocess.run(vtracer_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return False, f"vtracer error: {result.stderr}"

        return True, "Success"

    except Exception as e:
        return False, str(e)
