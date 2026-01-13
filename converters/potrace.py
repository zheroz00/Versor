"""
Potrace converter - outline tracing
Best for: solid shapes, silhouettes, CNC cutting
"""

import os
import subprocess
from config import POTRACE_PATH
from .dependencies import get_imagemagick_cmd
from .simplify import simplify_svg_file, straighten_svg_file
from .svg_to_dxf import convert_svg_to_dxf

# Potrace output format flags
POTRACE_FORMATS = {
    'svg': '-s',
    'dxf': '-b dxf',
    'pdf': '-b pdf',
    'eps': '-b eps'
}


def convert_with_potrace(input_path, output_path, corner_threshold=0, optimize_tolerance=0.1,
                         despeckle=2, threshold=50, invert=False,
                         simplify=False, simplify_tolerance=1.0,
                         straighten=False, straighten_tolerance=1.0,
                         output_format='svg'):
    """
    Convert a raster image to SVG/DXF/PDF/EPS using ImageMagick and Potrace.

    Produces outline paths that trace around the edges of shapes.

    Args:
        input_path: Path to input image
        output_path: Path for output file
        corner_threshold: Corner detection sensitivity (0=sharp, higher=rounded)
        optimize_tolerance: Curve optimization level
        despeckle: Noise removal threshold
        threshold: B/W conversion percentage
        invert: Whether to invert colors before tracing
        simplify: Whether to apply RDP path simplification (converts all to polylines)
        simplify_tolerance: Tolerance for RDP simplification (higher = more aggressive)
        straighten: Whether to convert nearly-straight curves to lines (preserves curves)
        straighten_tolerance: Tolerance for straightening (higher = more aggressive)
        output_format: Output format: 'svg', 'dxf', 'pdf', or 'eps'

    Returns:
        Tuple of (success: bool, message: str)
    """
    # Create temp BMP path
    bmp_path = input_path.rsplit('.', 1)[0] + '.bmp'
    # For post-processing with non-SVG output, we need SVG intermediate
    needs_postprocess = simplify or straighten
    use_svg_intermediate = needs_postprocess and output_format != 'svg'
    svg_intermediate_path = output_path.rsplit('.', 1)[0] + '_temp.svg' if use_svg_intermediate else None

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

        # Determine what format to generate first
        if use_svg_intermediate:
            # Generate SVG first for post-processing, then convert to target format
            initial_output = svg_intermediate_path
            format_flag = '-s'  # SVG
        else:
            initial_output = output_path
            format_flag = POTRACE_FORMATS.get(output_format, '-s')

        # Build Potrace command
        potrace_cmd = [
            POTRACE_PATH,
            bmp_path,
            "-a", str(corner_threshold),
            "-O", str(optimize_tolerance),
            "-t", str(despeckle),
            "-o", initial_output
        ]
        # Add format flag (split if it has multiple parts like '-b dxf')
        potrace_cmd[2:2] = format_flag.split()

        result = subprocess.run(potrace_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return False, f"Potrace error: {result.stderr}"

        # Apply post-processing (works on SVG)
        svg_to_process = svg_intermediate_path if use_svg_intermediate else output_path

        if needs_postprocess and (output_format == 'svg' or use_svg_intermediate):
            # Apply smart straightening first (preserves curves)
            if straighten:
                success, msg = straighten_svg_file(svg_to_process, svg_to_process, straighten_tolerance)
                if not success:
                    return False, f"Straightening error: {msg}"

            # Then apply RDP simplification if also requested (converts to polylines)
            if simplify:
                success, msg = simplify_svg_file(svg_to_process, svg_to_process, simplify_tolerance)
                if not success:
                    return False, f"Simplification error: {msg}"

        # Convert from SVG to target format if needed
        if use_svg_intermediate:
            if output_format == 'dxf':
                success, msg = convert_svg_to_dxf(svg_intermediate_path, output_path)
                if not success:
                    return False, f"DXF conversion error: {msg}"
            else:
                # For PDF/EPS, we can't easily convert from SVG
                # Fall back to regenerating without post-processing
                return False, f"Post-processing not supported for {output_format} format"

        return True, "Success"

    finally:
        # Clean up temp files
        if os.path.exists(bmp_path):
            os.remove(bmp_path)
        if svg_intermediate_path and os.path.exists(svg_intermediate_path):
            os.remove(svg_intermediate_path)
