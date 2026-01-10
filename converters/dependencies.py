"""
Dependency checking for all vectorization tools
"""

import os
import subprocess
import shutil
from config import POTRACE_PATH, AUTOTRACE_PATH, VTRACER_PATH


def get_imagemagick_cmd():
    """
    Get the ImageMagick command name.
    Returns 'magick' for v7+, 'convert' for v6, or None if not found.
    """
    if shutil.which('magick'):
        return 'magick'
    elif shutil.which('convert'):
        return 'convert'
    return None


def check_dependencies():
    """
    Verify all vectorization tools are available.

    Returns:
        Tuple of (errors: list, warnings: list)
        - errors: Critical issues that prevent basic functionality
        - warnings: Optional tools that are not available
    """
    errors = []
    warnings = []

    # Check Potrace (required)
    if not os.path.exists(POTRACE_PATH):
        errors.append(f"Potrace not found at: {POTRACE_PATH}")

    # Check ImageMagick (required) - supports both v6 (convert) and v7 (magick)
    im_cmd = get_imagemagick_cmd()
    if im_cmd is None:
        errors.append("ImageMagick not found (neither 'magick' nor 'convert' in PATH)")
    else:
        try:
            result = subprocess.run([im_cmd, "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                errors.append(f"ImageMagick '{im_cmd}' command failed")
        except FileNotFoundError:
            errors.append(f"ImageMagick '{im_cmd}' command not found")

    # Check Autotrace (optional - centerline)
    if not os.path.exists(AUTOTRACE_PATH):
        warnings.append(f"Autotrace not found at: {AUTOTRACE_PATH} (centerline tracing disabled)")

    # Check vtracer (optional)
    if not os.path.exists(VTRACER_PATH):
        warnings.append(f"vtracer not found at: {VTRACER_PATH} (vtracer method disabled)")

    return errors, warnings


def get_available_methods():
    """
    Check which conversion methods are available.

    Returns:
        Dict of method name -> bool (available)
    """
    return {
        'potrace': os.path.exists(POTRACE_PATH),
        'centerline': os.path.exists(AUTOTRACE_PATH),
        'vtracer': os.path.exists(VTRACER_PATH)
    }
