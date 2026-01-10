# Vector Converter

A local web application for converting raster images to SVG files. Built for CNC and laser cutting workflows, but useful for anyone who needs clean vector output.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-2.0+-green)
![Docker](https://img.shields.io/badge/Docker-supported-blue)

## What It Does

Converts PNG, JPG, BMP, and GIF images to SVG using three different methods:

| Method | Best For | How It Works |
|--------|----------|--------------|
| **Potrace** | CNC cutting, silhouettes | Traces outlines around shapes |
| **Centerline** | Engraving, line art, text | Traces through the middle of strokes |
| **vtracer** | Color artwork, illustrations | Preserves colors as separate paths |

Each method has presets optimized for common use cases, plus custom settings for fine-tuning.

## Requirements

- Python 3.10+
- [ImageMagick](https://imagemagick.org/) (required)
- [Potrace](http://potrace.sourceforge.net/) (required)
- [Autotrace](http://autotrace.sourceforge.net/) (optional, for centerline mode)
- [vtracer](https://github.com/visioncortex/vtracer) (optional, for color tracing)

Or just use Docker and skip the dependency hassle.

## Quick Start

### Docker (recommended)

```bash
docker compose up -d
```

Open http://localhost:5555 in your browser.

### Local

Install the external tools first, then: (Use uv or pip)

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
python app.py
```

Open http://localhost:5000 in your browser.

### Windows

PowerShell scripts are included for convenience:

```powershell
.\Start-Vectorizer.ps1   # Start server and open browser
.\Stop-Vectorizer.ps1    # Stop server
```

## Configuration

Tool paths can be set via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `POTRACE_PATH` | `/usr/bin/potrace` | Path to potrace binary |
| `AUTOTRACE_PATH` | `/usr/bin/autotrace` | Path to autotrace binary |
| `VTRACER_PATH` | `/usr/local/bin/vtracer` | Path to vtracer binary |
| `FLASK_HOST` | `127.0.0.1` | Bind address |
| `FLASK_DEBUG` | `true` | Enable debug mode |

## How It Works

```
Potrace:    Image → ImageMagick (threshold) → Potrace → SVG
Centerline: Image → ImageMagick (threshold) → Autotrace → SVG
vtracer:    Image → vtracer (direct) → SVG
```

The web UI shows a side-by-side comparison of the original image and the converted SVG.

## Project Structure

```
vector_converter/
├── app.py                 # Flask routes
├── config.py              # Tool paths and folders
├── presets.py             # Preset configurations
├── converters/            # Conversion logic
│   ├── potrace.py
│   ├── centerline.py
│   ├── vtracer.py
│   └── dependencies.py
├── static/                # CSS and JavaScript
├── templates/             # HTML templates
├── Dockerfile
└── docker compose.yml
```

## License

This project is licensed under the [Business Source License 1.1](LICENSE).

- **Non-Commercial Use:** Free for individuals, hobbyists, and educational purposes.
- **Commercial Use:** Restricted until the Change Date.
- **Change Date:** 2029-01-10.
- **Change License:** Apache License, Version 2.0.

After the Change Date, the software automatically becomes fully Open Source under the Apache 2.0 license.

## Contributing

Issues and pull requests welcome. This is a personal project, so response times may vary.
