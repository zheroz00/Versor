"""
Configuration for Versor
Tool paths, folders, and environment settings
"""

import os
import tempfile

# Tool paths - Use environment variables or fall back to defaults
POTRACE_PATH = os.environ.get('POTRACE_PATH', '/usr/bin/potrace')
AUTOTRACE_PATH = os.environ.get('AUTOTRACE_PATH', '/usr/bin/autotrace')
VTRACER_PATH = os.environ.get('VTRACER_PATH', '/usr/local/bin/vtracer')

# Temp folders for uploads and outputs
UPLOAD_FOLDER = tempfile.mkdtemp(prefix="versor_")
OUTPUT_FOLDER = tempfile.mkdtemp(prefix="versor_out_")
