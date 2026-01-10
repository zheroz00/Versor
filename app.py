"""
Vector Converter - Local Web UI for image to SVG conversion
Supports multiple vectorization methods: Potrace, Centerline, vtracer
"""

import os
import base64
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory

from config import UPLOAD_FOLDER, OUTPUT_FOLDER
from presets import POTRACE_PRESETS, CENTERLINE_PRESETS, VTRACER_PRESETS
from converters import (
    convert_with_potrace,
    convert_with_centerline,
    convert_with_vtracer,
    check_dependencies,
    get_available_methods
)

app = Flask(__name__)


def get_potrace_settings(preset_key, form_data):
    """Extract Potrace settings from preset or custom values."""
    if preset_key == 'custom':
        return {
            'corner_threshold': float(form_data.get('corner_threshold', 0)),
            'optimize_tolerance': float(form_data.get('optimize_tolerance', 0.1)),
            'despeckle': int(form_data.get('despeckle', 2)),
            'threshold': int(form_data.get('threshold', 50)),
            'invert': form_data.get('invert') == 'true'
        }
    preset = POTRACE_PRESETS.get(preset_key, POTRACE_PRESETS['cnc_precise'])
    return {
        'corner_threshold': preset['corner_threshold'],
        'optimize_tolerance': preset['optimize_tolerance'],
        'despeckle': preset['despeckle'],
        'threshold': preset['threshold'],
        'invert': form_data.get('invert') == 'true'
    }


def get_centerline_settings(preset_key, form_data):
    """Extract centerline settings from preset or custom values."""
    if preset_key == 'custom':
        return {
            'despeckle_level': int(form_data.get('despeckle_level', 2)),
            'corner_threshold': int(form_data.get('cl_corner_threshold', 100)),
            'line_threshold': float(form_data.get('line_threshold', 1.0)),
            'threshold': int(form_data.get('threshold', 50)),
            'invert': form_data.get('invert') == 'true'
        }
    preset = CENTERLINE_PRESETS.get(preset_key, CENTERLINE_PRESETS['line_art'])
    return {
        'despeckle_level': preset['despeckle_level'],
        'corner_threshold': preset['corner_threshold'],
        'line_threshold': preset['line_threshold'],
        'threshold': preset['threshold'],
        'invert': form_data.get('invert') == 'true'
    }


def get_vtracer_settings(preset_key, form_data):
    """Extract vtracer settings from preset or custom values."""
    if preset_key == 'custom':
        return {
            'mode': form_data.get('mode', 'spline'),
            'color_precision': int(form_data.get('color_precision', 6)),
            'gradient_step': int(form_data.get('gradient_step', 8)),
            'corner_threshold': int(form_data.get('vt_corner_threshold', 60)),
            'segment_length': int(form_data.get('segment_length', 4)),
            'splice_threshold': int(form_data.get('splice_threshold', 45)),
            'filter_speckle': int(form_data.get('filter_speckle', 4))
        }
    preset = VTRACER_PRESETS.get(preset_key, VTRACER_PRESETS['smooth_color'])
    return {
        'mode': preset['mode'],
        'color_precision': preset['color_precision'],
        'gradient_step': preset['gradient_step'],
        'corner_threshold': preset['corner_threshold'],
        'segment_length': preset['segment_length'],
        'splice_threshold': preset['splice_threshold'],
        'filter_speckle': preset['filter_speckle']
    }


@app.route('/')
def index():
    """Main page."""
    dep_errors, dep_warnings = check_dependencies()
    available_methods = get_available_methods()

    return render_template('index.html',
                           potrace_presets=POTRACE_PRESETS,
                           centerline_presets=CENTERLINE_PRESETS,
                           vtracer_presets=VTRACER_PRESETS,
                           available_methods=available_methods,
                           dep_errors=dep_errors,
                           dep_warnings=dep_warnings)


@app.route('/convert', methods=['POST'])
def convert():
    """Handle file conversion with method selection."""

    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    method = request.form.get('method', 'potrace')
    preset_key = request.form.get('preset', 'cnc_precise')

    # Get settings and converter based on method
    if method == 'potrace':
        settings = get_potrace_settings(preset_key, request.form)
        convert_func = convert_with_potrace
    elif method == 'centerline':
        settings = get_centerline_settings(preset_key, request.form)
        convert_func = convert_with_centerline
    elif method == 'vtracer':
        settings = get_vtracer_settings(preset_key, request.form)
        convert_func = convert_with_vtracer
    else:
        return jsonify({'error': f'Unknown method: {method}'}), 400

    results = []

    for file in files:
        if file.filename == '':
            continue

        # Save uploaded file
        filename = Path(file.filename).name
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)

        # Read original image as base64 for preview (before conversion)
        original_preview = None
        input_size = os.path.getsize(input_path)
        if input_size < 15000000:  # < 15MB for original preview
            with open(input_path, 'rb') as f:
                img_data = f.read()
                # Detect mime type from extension
                ext = os.path.splitext(filename)[1].lower()
                mime_types = {'.png': 'image/png', '.jpg': 'image/jpeg',
                              '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.bmp': 'image/bmp'}
                mime_type = mime_types.get(ext, 'image/png')
                original_preview = f"data:{mime_type};base64,{base64.b64encode(img_data).decode('utf-8')}"

        # Generate output filename
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}.svg"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        # Convert
        success, message = convert_func(input_path, output_path, **settings)

        result = {
            'filename': filename,
            'output_filename': output_filename,
            'success': success,
            'message': message
        }

        # Include original image preview
        if original_preview:
            result['original_preview'] = original_preview

        # Include SVG preview if successful
        if success and os.path.exists(output_path):
            result['download_url'] = f'/download/{output_filename}'
            file_size = os.path.getsize(output_path)
            # Read SVG for inline preview (up to 2MB for color SVGs)
            if file_size < 2000000:  # < 2MB
                with open(output_path, 'r', encoding='utf-8', errors='ignore') as f:
                    result['svg_content'] = f.read()
            else:
                result['preview_unavailable_reason'] = f'File too large for preview ({file_size // 1024}KB)'

        results.append(result)

        # Clean up input file
        if os.path.exists(input_path):
            os.remove(input_path)

    return jsonify({'results': results})


@app.route('/download/<filename>')
def download(filename):
    """Download a converted SVG file."""
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


@app.route('/preview/<filename>')
def preview(filename):
    """Preview a converted SVG file in browser."""
    return send_from_directory(OUTPUT_FOLDER, filename, mimetype='image/svg+xml')


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  Vector Converter")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 50 + "\n")

    # Check dependencies on startup
    errors, warnings = check_dependencies()
    if errors:
        print("ERRORS (will affect functionality):")
        for e in errors:
            print(f"  - {e}")
        print()
    if warnings:
        print("WARNINGS (some features disabled):")
        for w in warnings:
            print(f"  - {w}")
        print()

    # Use 0.0.0.0 to allow access from Docker host
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    app.run(host=host, debug=debug, port=5000)
