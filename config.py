"""
Configuration for Vector Converter
Tool paths, folders, and environment settings
"""

import os
import tempfile

# Tool paths - Use environment variables or fall back to defaults
POTRACE_PATH = os.environ.get('POTRACE_PATH', r"C:\MyPrograms\potrace-1.16.win64\potrace.exe")
AUTOTRACE_PATH = os.environ.get('AUTOTRACE_PATH', '/usr/bin/autotrace')
VTRACER_PATH = os.environ.get('VTRACER_PATH', '/usr/local/bin/vtracer')

# Temp folders for uploads and outputs
UPLOAD_FOLDER = tempfile.mkdtemp(prefix="vectorizer_")
OUTPUT_FOLDER = tempfile.mkdtemp(prefix="vectorizer_out_")
