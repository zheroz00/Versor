"""
Presets for all vectorization methods
Each method has its own optimized presets
"""

# Potrace presets - outline tracing for CNC cutting
POTRACE_PRESETS = {
    "cnc_precise": {
        "name": "CNC Precise",
        "description": "Maximum accuracy for tool paths. Sharp corners, tight curves.",
        "corner_threshold": 0,
        "optimize_tolerance": 0.05,
        "despeckle": 1,
        "threshold": 50
    },
    "cnc_balanced": {
        "name": "CNC Balanced",
        "description": "Good accuracy with some smoothing. Recommended for most CNC work.",
        "corner_threshold": 0.3,
        "optimize_tolerance": 0.1,
        "despeckle": 2,
        "threshold": 50
    },
    "clean_output": {
        "name": "Clean Output",
        "description": "Minimal nodes for clean B&W art. Sharp corners, optimized paths.",
        "corner_threshold": 0,
        "optimize_tolerance": 0.02,
        "despeckle": 1,
        "threshold": 50
    },
    "smooth": {
        "name": "Smooth Lines",
        "description": "Cleaner output, reduces noise. Good for rough scans or sketchy line art.",
        "corner_threshold": 0.5,
        "optimize_tolerance": 0.1,
        "despeckle": 5,
        "threshold": 50
    },
    "simplified": {
        "name": "Simplified",
        "description": "Fewer nodes, smoother curves. Reduces complexity significantly.",
        "corner_threshold": 1.0,
        "optimize_tolerance": 0.5,
        "despeckle": 10,
        "threshold": 50
    },
    "custom": {
        "name": "Custom",
        "description": "Set your own parameters.",
        "corner_threshold": 0,
        "optimize_tolerance": 0.1,
        "despeckle": 2,
        "threshold": 50
    }
}

# Centerline presets - single-line tracing for engraving
CENTERLINE_PRESETS = {
    "line_art": {
        "name": "Line Art",
        "description": "Clean single lines for sketches and drawings.",
        "despeckle_level": 2,
        "corner_threshold": 100,
        "line_threshold": 1.0,
        "threshold": 50
    },
    "text_engrave": {
        "name": "Text Engraving",
        "description": "Optimized for text and lettering paths.",
        "despeckle_level": 3,
        "corner_threshold": 120,
        "line_threshold": 0.5,
        "threshold": 45
    },
    "technical": {
        "name": "Technical Drawing",
        "description": "Precise centerlines for technical illustrations.",
        "despeckle_level": 1,
        "corner_threshold": 80,
        "line_threshold": 0.8,
        "threshold": 50
    },
    "sketch": {
        "name": "Sketch",
        "description": "Forgiving settings for hand-drawn sketches.",
        "despeckle_level": 5,
        "corner_threshold": 110,
        "line_threshold": 1.5,
        "threshold": 55
    },
    "custom": {
        "name": "Custom",
        "description": "Set your own centerline parameters.",
        "despeckle_level": 2,
        "corner_threshold": 100,
        "line_threshold": 1.0,
        "threshold": 50
    }
}

# vtracer presets - color/detail tracing
VTRACER_PRESETS = {
    "detailed": {
        "name": "Detailed",
        "description": "Maximum detail preservation for complex artwork.",
        "mode": "polygon",
        "color_precision": 8,
        "gradient_step": 6,
        "corner_threshold": 60,
        "segment_length": 4,
        "splice_threshold": 45,
        "filter_speckle": 2
    },
    "pixel_art": {
        "name": "Pixel Art",
        "description": "Sharp edges for pixel-style graphics.",
        "mode": "pixel",
        "color_precision": 6,
        "gradient_step": 4,
        "corner_threshold": 90,
        "segment_length": 4,
        "splice_threshold": 45,
        "filter_speckle": 0
    },
    "smooth_color": {
        "name": "Smooth Color",
        "description": "Smooth curves for illustrations and logos.",
        "mode": "spline",
        "color_precision": 6,
        "gradient_step": 8,
        "corner_threshold": 45,
        "segment_length": 6,
        "splice_threshold": 45,
        "filter_speckle": 4
    },
    "simple": {
        "name": "Simplified",
        "description": "Fewer colors and shapes for cleaner output.",
        "mode": "spline",
        "color_precision": 4,
        "gradient_step": 16,
        "corner_threshold": 60,
        "segment_length": 8,
        "splice_threshold": 45,
        "filter_speckle": 8
    },
    "custom": {
        "name": "Custom",
        "description": "Set your own vtracer parameters.",
        "mode": "spline",
        "color_precision": 6,
        "gradient_step": 8,
        "corner_threshold": 60,
        "segment_length": 4,
        "splice_threshold": 45,
        "filter_speckle": 4
    }
}
