# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Versor is a local web application for converting raster images (PNG, JPG, BMP, GIF) to SVG files, optimized for CNC tool path generation. It supports three vectorization methods:

- **Potrace**: Outline tracing for CNC cutting (traces around shapes)
- **Centerline**: Single-line tracing for engraving (traces through middle of strokes)
- **vtracer**: Color/detail tracing for artwork and illustrations

## Running the Application

**Local development:**
```bash
python app.py
```
Opens at http://localhost:5000

**Windows convenience scripts:**
```powershell
.\Start-Versor.ps1  # Starts server in background, opens browser
.\Stop-Versor.ps1   # Stops the server
```

**Docker:**
```bash
docker compose up
```

## External Dependencies

Required:
- **ImageMagick**: Must be installed with `magick` command in PATH
- **Potrace**: Path via `POTRACE_PATH` env var (default: Windows path locally, `/usr/bin/potrace` in Docker)

Optional (enable additional methods):
- **Autotrace**: Path via `AUTOTRACE_PATH` env var (enables centerline tracing)
- **vtracer**: Path via `VTRACER_PATH` env var (enables color/detail tracing)

## Architecture

**Project Structure:**
```
Versor/
├── app.py                 # Flask routes and settings extraction
├── config.py              # Tool paths and folder configuration
├── presets.py             # Presets for all three methods
├── converters/
│   ├── __init__.py        # Package exports
│   ├── potrace.py         # Outline tracing
│   ├── centerline.py      # Single-line tracing
│   ├── vtracer.py         # Color/detail tracing
│   └── dependencies.py    # Tool availability checking
├── static/
│   ├── css/style.css      # All CSS styles
│   └── js/app.js          # Frontend JavaScript
├── templates/
│   └── index.html         # HTML with tabbed UI
├── Dockerfile
└── docker compose.yml
```

**Conversion Pipelines:**
```
Potrace:    Image → ImageMagick (threshold to BMP) → Potrace → SVG
Centerline: Image → ImageMagick (threshold to PBM) → Autotrace (-centerline) → SVG
vtracer:    Image → vtracer (direct) → SVG
```

**Presets System:**

Each method has its own optimized presets:

| Method | Presets |
|--------|---------|
| Potrace | cnc_precise, cnc_balanced, smooth, simplified, custom |
| Centerline | line_art, text_engrave, technical, sketch, custom |
| vtracer | detailed, pixel_art, smooth_color, simple, custom |

**Key Parameters by Method:**

Potrace:
- `corner_threshold` (-a): Corner detection sensitivity
- `optimize_tolerance` (-O): Curve optimization level
- `despeckle` (-t): Noise removal threshold

Centerline:
- `despeckle_level`: Noise removal (0-20)
- `corner_threshold`: Corner detection angle (degrees)
- `line_threshold`: Minimum line length

vtracer:
- `mode`: polygon (sharp) or spline (smooth)
- `color_precision`: Color depth (1-8)
- `layer_difference`: Color grouping threshold

**Temp File Handling:** Uploads and outputs use `tempfile.mkdtemp()` directories. Input files are cleaned after conversion; output SVGs persist for download.

## When to Use Each Method

| Use Case | Method | Why |
|----------|--------|-----|
| CNC cutting shapes | Potrace | Clean outlines for cutting paths |
| Engraving line art | Centerline | Single pass instead of double outline |
| Engraving text | Centerline | Cleaner, faster text engraving |
| Color logos | vtracer | Preserves colors as separate paths |
| Pixel art | vtracer (polygon mode) | Keeps sharp pixel edges |
| Detailed artwork | vtracer | Handles complex color gradients |
