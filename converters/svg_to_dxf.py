"""
SVG to DXF converter for post-processed output.
Converts SVG paths to DXF polylines, preserving the clean node structure.
"""

import re
import math


def parse_svg_path(d):
    """Parse SVG path data into commands."""
    command_pattern = re.compile(r'([MmLlHhVvCcSsQqTtAaZz])')
    number_pattern = re.compile(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')

    tokens = command_pattern.split(d)
    commands = []

    i = 1
    while i < len(tokens):
        cmd = tokens[i]
        args_str = tokens[i + 1] if i + 1 < len(tokens) else ''
        args = [float(x) for x in number_pattern.findall(args_str)]
        commands.append((cmd, args))
        i += 2

    return commands


def svg_path_to_polylines(d):
    """
    Convert SVG path data to a list of polylines.
    Each polyline is a list of (x, y) tuples.
    Returns list of (points, is_closed) tuples.
    """
    commands = parse_svg_path(d)
    polylines = []
    current_points = []

    x, y = 0, 0
    start_x, start_y = 0, 0

    for cmd, args in commands:
        if cmd == 'M':
            if current_points:
                polylines.append((current_points, False))
            current_points = []
            x, y = args[0], args[1]
            start_x, start_y = x, y
            current_points.append((x, y))
            # Implicit lineto after M
            for i in range(2, len(args), 2):
                x, y = args[i], args[i + 1]
                current_points.append((x, y))

        elif cmd == 'm':
            if current_points:
                polylines.append((current_points, False))
            current_points = []
            x += args[0]
            y += args[1]
            start_x, start_y = x, y
            current_points.append((x, y))
            for i in range(2, len(args), 2):
                x += args[i]
                y += args[i + 1]
                current_points.append((x, y))

        elif cmd == 'L':
            for i in range(0, len(args), 2):
                x, y = args[i], args[i + 1]
                current_points.append((x, y))

        elif cmd == 'l':
            for i in range(0, len(args), 2):
                x += args[i]
                y += args[i + 1]
                current_points.append((x, y))

        elif cmd == 'H':
            for val in args:
                x = val
                current_points.append((x, y))

        elif cmd == 'h':
            for val in args:
                x += val
                current_points.append((x, y))

        elif cmd == 'V':
            for val in args:
                y = val
                current_points.append((x, y))

        elif cmd == 'v':
            for val in args:
                y += val
                current_points.append((x, y))

        elif cmd == 'C':
            # Cubic bezier - sample at intervals for DXF
            for i in range(0, len(args), 6):
                p0 = (x, y)
                p1 = (args[i], args[i + 1])
                p2 = (args[i + 2], args[i + 3])
                p3 = (args[i + 4], args[i + 5])
                # Sample the bezier curve
                for t in [0.25, 0.5, 0.75, 1.0]:
                    px, py = cubic_bezier_point(p0, p1, p2, p3, t)
                    current_points.append((px, py))
                x, y = p3

        elif cmd == 'c':
            for i in range(0, len(args), 6):
                p0 = (x, y)
                p1 = (x + args[i], y + args[i + 1])
                p2 = (x + args[i + 2], y + args[i + 3])
                p3 = (x + args[i + 4], y + args[i + 5])
                for t in [0.25, 0.5, 0.75, 1.0]:
                    px, py = cubic_bezier_point(p0, p1, p2, p3, t)
                    current_points.append((px, py))
                x, y = p3

        elif cmd == 'Q':
            # Quadratic bezier
            for i in range(0, len(args), 4):
                p0 = (x, y)
                p1 = (args[i], args[i + 1])
                p2 = (args[i + 2], args[i + 3])
                for t in [0.25, 0.5, 0.75, 1.0]:
                    px, py = quad_bezier_point(p0, p1, p2, t)
                    current_points.append((px, py))
                x, y = p2

        elif cmd == 'q':
            for i in range(0, len(args), 4):
                p0 = (x, y)
                p1 = (x + args[i], y + args[i + 1])
                p2 = (x + args[i + 2], y + args[i + 3])
                for t in [0.25, 0.5, 0.75, 1.0]:
                    px, py = quad_bezier_point(p0, p1, p2, t)
                    current_points.append((px, py))
                x, y = p2

        elif cmd in ('Z', 'z'):
            # Close path
            if current_points and (x != start_x or y != start_y):
                current_points.append((start_x, start_y))
            if current_points:
                polylines.append((current_points, True))
            current_points = []
            x, y = start_x, start_y

    # Handle unclosed path
    if current_points:
        polylines.append((current_points, False))

    return polylines


def cubic_bezier_point(p0, p1, p2, p3, t):
    """Calculate point on cubic bezier at parameter t."""
    mt = 1 - t
    x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
    y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
    return (x, y)


def quad_bezier_point(p0, p1, p2, t):
    """Calculate point on quadratic bezier at parameter t."""
    mt = 1 - t
    x = mt**2 * p0[0] + 2 * mt * t * p1[0] + t**2 * p2[0]
    y = mt**2 * p0[1] + 2 * mt * t * p1[1] + t**2 * p2[1]
    return (x, y)


def extract_svg_dimensions(svg_content):
    """Extract viewBox or width/height from SVG."""
    # Try viewBox first
    viewbox_match = re.search(r'viewBox\s*=\s*"([^"]+)"', svg_content)
    if viewbox_match:
        parts = viewbox_match.group(1).split()
        if len(parts) >= 4:
            return float(parts[2]), float(parts[3])

    # Fall back to width/height
    width_match = re.search(r'width\s*=\s*"([\d.]+)', svg_content)
    height_match = re.search(r'height\s*=\s*"([\d.]+)', svg_content)
    if width_match and height_match:
        return float(width_match.group(1)), float(height_match.group(1))

    return 100, 100  # Default


def convert_svg_to_dxf(input_path, output_path):
    """
    Convert an SVG file to DXF format.

    Args:
        input_path: Path to input SVG file
        output_path: Path for output DXF file

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        with open(input_path, 'r') as f:
            svg_content = f.read()

        width, height = extract_svg_dimensions(svg_content)

        # Extract all path d attributes
        path_pattern = re.compile(r'<path[^>]*\sd="([^"]+)"', re.IGNORECASE)
        paths = path_pattern.findall(svg_content)

        all_polylines = []
        for path_d in paths:
            polylines = svg_path_to_polylines(path_d)
            all_polylines.extend(polylines)

        # Generate DXF content
        dxf_content = generate_dxf(all_polylines, width, height)

        with open(output_path, 'w') as f:
            f.write(dxf_content)

        return True, "Success"

    except Exception as e:
        return False, str(e)


def generate_dxf(polylines, width, height):
    """Generate DXF file content from polylines."""
    lines = []

    # DXF Header
    lines.extend([
        "0", "SECTION",
        "2", "HEADER",
        "9", "$ACADVER",
        "1", "AC1015",  # AutoCAD 2000
        "9", "$INSBASE",
        "10", "0.0",
        "20", "0.0",
        "30", "0.0",
        "9", "$EXTMIN",
        "10", "0.0",
        "20", "0.0",
        "30", "0.0",
        "9", "$EXTMAX",
        "10", str(width),
        "20", str(height),
        "30", "0.0",
        "0", "ENDSEC",
    ])

    # Tables section (minimal)
    lines.extend([
        "0", "SECTION",
        "2", "TABLES",
        "0", "TABLE",
        "2", "LAYER",
        "70", "1",
        "0", "LAYER",
        "2", "0",
        "70", "0",
        "62", "7",
        "6", "CONTINUOUS",
        "0", "ENDTAB",
        "0", "ENDSEC",
    ])

    # Entities section
    lines.extend([
        "0", "SECTION",
        "2", "ENTITIES",
    ])

    # Add polylines
    for points, is_closed in polylines:
        if len(points) < 2:
            continue

        # Flip Y coordinates (SVG has Y down, DXF has Y up)
        flipped_points = [(x, height - y) for x, y in points]

        lines.extend([
            "0", "LWPOLYLINE",
            "8", "0",  # Layer
            "90", str(len(flipped_points)),  # Number of vertices
            "70", "1" if is_closed else "0",  # Closed flag
        ])

        for x, y in flipped_points:
            lines.extend([
                "10", f"{x:.6f}",
                "20", f"{y:.6f}",
            ])

    lines.extend([
        "0", "ENDSEC",
        "0", "EOF",
    ])

    return "\n".join(lines)
