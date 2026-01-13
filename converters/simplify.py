"""
SVG path simplification using Ramer-Douglas-Peucker algorithm.
Reduces node count while preserving shape geometry.
"""

import re
import math


def perpendicular_distance(point, line_start, line_end):
    """Calculate perpendicular distance from a point to a line segment."""
    x, y = point
    x1, y1 = line_start
    x2, y2 = line_end

    # Handle case where line_start == line_end
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.sqrt((x - x1) ** 2 + (y - y1) ** 2)

    # Calculate perpendicular distance
    numerator = abs(dy * x - dx * y + x2 * y1 - y2 * x1)
    denominator = math.sqrt(dx ** 2 + dy ** 2)
    return numerator / denominator


def rdp_simplify(points, epsilon):
    """
    Ramer-Douglas-Peucker algorithm for path simplification.

    Args:
        points: List of (x, y) tuples
        epsilon: Maximum distance threshold for point removal

    Returns:
        Simplified list of (x, y) tuples
    """
    if len(points) < 3:
        return points

    # Find the point with the maximum distance from the line
    max_dist = 0
    max_idx = 0
    for i in range(1, len(points) - 1):
        dist = perpendicular_distance(points[i], points[0], points[-1])
        if dist > max_dist:
            max_dist = dist
            max_idx = i

    # If max distance is greater than epsilon, recursively simplify
    if max_dist > epsilon:
        # Recursive call
        left = rdp_simplify(points[:max_idx + 1], epsilon)
        right = rdp_simplify(points[max_idx:], epsilon)
        # Concatenate results (avoiding duplicate point at max_idx)
        return left[:-1] + right
    else:
        # All points between first and last can be removed
        return [points[0], points[-1]]


def parse_svg_path(d):
    """
    Parse SVG path data into a list of commands and coordinates.
    Returns list of (command, points) tuples.
    """
    # Regex to match path commands and their arguments
    command_pattern = re.compile(r'([MmLlHhVvCcSsQqTtAaZz])')
    number_pattern = re.compile(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')

    commands = []
    tokens = command_pattern.split(d)

    i = 1  # Skip first empty string
    while i < len(tokens):
        cmd = tokens[i]
        args_str = tokens[i + 1] if i + 1 < len(tokens) else ''
        args = [float(x) for x in number_pattern.findall(args_str)]
        commands.append((cmd, args))
        i += 2

    return commands


def path_to_points(commands):
    """
    Convert SVG path commands to a list of absolute points.
    Also returns info about subpaths for reconstruction.
    """
    points = []
    subpaths = []  # List of (start_idx, end_idx, is_closed)
    current_subpath_start = 0

    x, y = 0, 0  # Current position
    start_x, start_y = 0, 0  # Start of current subpath

    for cmd, args in commands:
        if cmd == 'M':
            # Start new subpath
            if points:
                subpaths.append((current_subpath_start, len(points) - 1, False))
            current_subpath_start = len(points)
            x, y = args[0], args[1]
            start_x, start_y = x, y
            points.append((x, y))
            # Handle implicit lineto commands after M
            for i in range(2, len(args), 2):
                x, y = args[i], args[i + 1]
                points.append((x, y))
        elif cmd == 'm':
            if points:
                subpaths.append((current_subpath_start, len(points) - 1, False))
            current_subpath_start = len(points)
            x += args[0]
            y += args[1]
            start_x, start_y = x, y
            points.append((x, y))
            for i in range(2, len(args), 2):
                x += args[i]
                y += args[i + 1]
                points.append((x, y))
        elif cmd == 'L':
            for i in range(0, len(args), 2):
                x, y = args[i], args[i + 1]
                points.append((x, y))
        elif cmd == 'l':
            for i in range(0, len(args), 2):
                x += args[i]
                y += args[i + 1]
                points.append((x, y))
        elif cmd == 'H':
            for val in args:
                x = val
                points.append((x, y))
        elif cmd == 'h':
            for val in args:
                x += val
                points.append((x, y))
        elif cmd == 'V':
            for val in args:
                y = val
                points.append((x, y))
        elif cmd == 'v':
            for val in args:
                y += val
                points.append((x, y))
        elif cmd == 'C':
            # Cubic bezier - sample it for simplification
            for i in range(0, len(args), 6):
                # Just use endpoint for simplification (we'll lose curve info)
                x, y = args[i + 4], args[i + 5]
                points.append((x, y))
        elif cmd == 'c':
            for i in range(0, len(args), 6):
                x += args[i + 4]
                y += args[i + 5]
                points.append((x, y))
        elif cmd in ('Z', 'z'):
            # Close path
            if points and (x != start_x or y != start_y):
                points.append((start_x, start_y))
            subpaths.append((current_subpath_start, len(points) - 1, True))
            current_subpath_start = len(points)
            x, y = start_x, start_y

    # Handle last subpath if not closed
    if current_subpath_start < len(points):
        subpaths.append((current_subpath_start, len(points) - 1, False))

    return points, subpaths


def points_to_path(points, subpaths):
    """Convert simplified points back to SVG path data."""
    if not points or not subpaths:
        return ""

    path_parts = []

    for start_idx, end_idx, is_closed in subpaths:
        if start_idx > end_idx:
            continue

        subpath_points = points[start_idx:end_idx + 1]
        if not subpath_points:
            continue

        # Start with moveto
        x, y = subpath_points[0]
        parts = [f"M{x:.2f} {y:.2f}"]

        # Add lineto commands for remaining points
        for px, py in subpath_points[1:]:
            parts.append(f"L{px:.2f} {py:.2f}")

        # Close path if it was originally closed
        if is_closed:
            parts.append("Z")

        path_parts.append(" ".join(parts))

    return " ".join(path_parts)


def simplify_svg_path(d, epsilon=1.0):
    """
    Simplify an SVG path string using RDP algorithm.

    Args:
        d: SVG path data string
        epsilon: Simplification tolerance (higher = more aggressive)

    Returns:
        Simplified SVG path data string
    """
    commands = parse_svg_path(d)
    points, subpaths = path_to_points(commands)

    if len(points) < 3:
        return d

    # Simplify each subpath independently
    simplified_points = []
    new_subpaths = []

    for start_idx, end_idx, is_closed in subpaths:
        subpath_points = points[start_idx:end_idx + 1]

        if len(subpath_points) < 3:
            # Can't simplify, keep as-is
            new_start = len(simplified_points)
            simplified_points.extend(subpath_points)
            new_subpaths.append((new_start, len(simplified_points) - 1, is_closed))
        else:
            # Apply RDP simplification
            simplified = rdp_simplify(subpath_points, epsilon)
            new_start = len(simplified_points)
            simplified_points.extend(simplified)
            new_subpaths.append((new_start, len(simplified_points) - 1, is_closed))

    return points_to_path(simplified_points, new_subpaths)


def simplify_svg_file(input_path, output_path, epsilon=1.0):
    """
    Simplify all paths in an SVG file.

    Args:
        input_path: Path to input SVG file
        output_path: Path for output SVG file
        epsilon: Simplification tolerance (higher = more aggressive)

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        with open(input_path, 'r') as f:
            svg_content = f.read()

        # Find and simplify all path d attributes
        path_pattern = re.compile(r'(<path[^>]*\sd=")([^"]+)("[^>]*>)', re.IGNORECASE)

        def replace_path(match):
            prefix = match.group(1)
            d = match.group(2)
            suffix = match.group(3)
            simplified_d = simplify_svg_path(d, epsilon)
            return prefix + simplified_d + suffix

        simplified_svg = path_pattern.sub(replace_path, svg_content)

        with open(output_path, 'w') as f:
            f.write(simplified_svg)

        return True, "Success"

    except Exception as e:
        return False, str(e)


# =============================================================================
# Smart Straightening - Converts nearly-straight Beziers to lines
# =============================================================================

def bezier_control_deviation(p0, p1, p2, p3):
    """
    Calculate max deviation of control points from the line between endpoints.
    For cubic Bezier: P0 (start), P1, P2 (control points), P3 (end)
    Returns the maximum perpendicular distance of P1 and P2 from line P0-P3.
    """
    dist1 = perpendicular_distance(p1, p0, p3)
    dist2 = perpendicular_distance(p2, p0, p3)
    return max(dist1, dist2)


def straighten_svg_path(d, tolerance=1.0):
    """
    Smart straightening: converts nearly-straight Bezier curves to lines
    while preserving actual curves.

    Args:
        d: SVG path data string
        tolerance: Maximum control point deviation to consider a curve "straight"

    Returns:
        Optimized SVG path data string with straight segments as lines
    """
    command_pattern = re.compile(r'([MmLlHhVvCcSsQqTtAaZz])')
    number_pattern = re.compile(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')

    tokens = command_pattern.split(d)
    result_parts = []

    x, y = 0, 0  # Current position
    start_x, start_y = 0, 0  # Subpath start
    last_control = None  # For smooth curve commands (S, s)

    i = 1
    while i < len(tokens):
        cmd = tokens[i]
        args_str = tokens[i + 1] if i + 1 < len(tokens) else ''
        args = [float(n) for n in number_pattern.findall(args_str)]
        i += 2

        if cmd == 'M':
            x, y = args[0], args[1]
            start_x, start_y = x, y
            result_parts.append(f"M{x:.2f} {y:.2f}")
            # Implicit lineto after M
            for j in range(2, len(args), 2):
                x, y = args[j], args[j + 1]
                result_parts.append(f"L{x:.2f} {y:.2f}")
            last_control = None

        elif cmd == 'm':
            x += args[0]
            y += args[1]
            start_x, start_y = x, y
            result_parts.append(f"M{x:.2f} {y:.2f}")
            for j in range(2, len(args), 2):
                x += args[j]
                y += args[j + 1]
                result_parts.append(f"L{x:.2f} {y:.2f}")
            last_control = None

        elif cmd == 'L':
            for j in range(0, len(args), 2):
                x, y = args[j], args[j + 1]
                result_parts.append(f"L{x:.2f} {y:.2f}")
            last_control = None

        elif cmd == 'l':
            for j in range(0, len(args), 2):
                x += args[j]
                y += args[j + 1]
                result_parts.append(f"L{x:.2f} {y:.2f}")
            last_control = None

        elif cmd == 'H':
            for val in args:
                x = val
                result_parts.append(f"L{x:.2f} {y:.2f}")
            last_control = None

        elif cmd == 'h':
            for val in args:
                x += val
                result_parts.append(f"L{x:.2f} {y:.2f}")
            last_control = None

        elif cmd == 'V':
            for val in args:
                y = val
                result_parts.append(f"L{x:.2f} {y:.2f}")
            last_control = None

        elif cmd == 'v':
            for val in args:
                y += val
                result_parts.append(f"L{x:.2f} {y:.2f}")
            last_control = None

        elif cmd == 'C':
            # Cubic Bezier - check if essentially straight
            for j in range(0, len(args), 6):
                p0 = (x, y)
                p1 = (args[j], args[j + 1])
                p2 = (args[j + 2], args[j + 3])
                p3 = (args[j + 4], args[j + 5])

                deviation = bezier_control_deviation(p0, p1, p2, p3)
                if deviation <= tolerance:
                    # Nearly straight - use line
                    result_parts.append(f"L{p3[0]:.2f} {p3[1]:.2f}")
                else:
                    # Keep as curve
                    result_parts.append(
                        f"C{p1[0]:.2f} {p1[1]:.2f} {p2[0]:.2f} {p2[1]:.2f} {p3[0]:.2f} {p3[1]:.2f}"
                    )
                x, y = p3
                last_control = p2

        elif cmd == 'c':
            for j in range(0, len(args), 6):
                p0 = (x, y)
                p1 = (x + args[j], y + args[j + 1])
                p2 = (x + args[j + 2], y + args[j + 3])
                p3 = (x + args[j + 4], y + args[j + 5])

                deviation = bezier_control_deviation(p0, p1, p2, p3)
                if deviation <= tolerance:
                    result_parts.append(f"L{p3[0]:.2f} {p3[1]:.2f}")
                else:
                    result_parts.append(
                        f"C{p1[0]:.2f} {p1[1]:.2f} {p2[0]:.2f} {p2[1]:.2f} {p3[0]:.2f} {p3[1]:.2f}"
                    )
                x, y = p3
                last_control = p2

        elif cmd == 'S':
            # Smooth cubic - first control point is reflection of previous
            for j in range(0, len(args), 4):
                p0 = (x, y)
                if last_control:
                    p1 = (2 * x - last_control[0], 2 * y - last_control[1])
                else:
                    p1 = p0
                p2 = (args[j], args[j + 1])
                p3 = (args[j + 2], args[j + 3])

                deviation = bezier_control_deviation(p0, p1, p2, p3)
                if deviation <= tolerance:
                    result_parts.append(f"L{p3[0]:.2f} {p3[1]:.2f}")
                else:
                    result_parts.append(
                        f"C{p1[0]:.2f} {p1[1]:.2f} {p2[0]:.2f} {p2[1]:.2f} {p3[0]:.2f} {p3[1]:.2f}"
                    )
                x, y = p3
                last_control = p2

        elif cmd == 's':
            for j in range(0, len(args), 4):
                p0 = (x, y)
                if last_control:
                    p1 = (2 * x - last_control[0], 2 * y - last_control[1])
                else:
                    p1 = p0
                p2 = (x + args[j], y + args[j + 1])
                p3 = (x + args[j + 2], y + args[j + 3])

                deviation = bezier_control_deviation(p0, p1, p2, p3)
                if deviation <= tolerance:
                    result_parts.append(f"L{p3[0]:.2f} {p3[1]:.2f}")
                else:
                    result_parts.append(
                        f"C{p1[0]:.2f} {p1[1]:.2f} {p2[0]:.2f} {p2[1]:.2f} {p3[0]:.2f} {p3[1]:.2f}"
                    )
                x, y = p3
                last_control = p2

        elif cmd == 'Q':
            # Quadratic Bezier - convert to check, keep as Q if curved
            for j in range(0, len(args), 4):
                p0 = (x, y)
                p1 = (args[j], args[j + 1])  # Control point
                p2 = (args[j + 2], args[j + 3])  # End point

                deviation = perpendicular_distance(p1, p0, p2)
                if deviation <= tolerance:
                    result_parts.append(f"L{p2[0]:.2f} {p2[1]:.2f}")
                else:
                    result_parts.append(
                        f"Q{p1[0]:.2f} {p1[1]:.2f} {p2[0]:.2f} {p2[1]:.2f}"
                    )
                x, y = p2
            last_control = None

        elif cmd == 'q':
            for j in range(0, len(args), 4):
                p0 = (x, y)
                p1 = (x + args[j], y + args[j + 1])
                p2 = (x + args[j + 2], y + args[j + 3])

                deviation = perpendicular_distance(p1, p0, p2)
                if deviation <= tolerance:
                    result_parts.append(f"L{p2[0]:.2f} {p2[1]:.2f}")
                else:
                    result_parts.append(
                        f"Q{p1[0]:.2f} {p1[1]:.2f} {p2[0]:.2f} {p2[1]:.2f}"
                    )
                x, y = p2
            last_control = None

        elif cmd in ('Z', 'z'):
            result_parts.append("Z")
            x, y = start_x, start_y
            last_control = None

        elif cmd in ('A', 'a'):
            # Arc commands - pass through unchanged
            if cmd == 'A':
                for j in range(0, len(args), 7):
                    rx, ry = args[j], args[j + 1]
                    rotation = args[j + 2]
                    large_arc = int(args[j + 3])
                    sweep = int(args[j + 4])
                    ex, ey = args[j + 5], args[j + 6]
                    result_parts.append(
                        f"A{rx:.2f} {ry:.2f} {rotation:.2f} {large_arc} {sweep} {ex:.2f} {ey:.2f}"
                    )
                    x, y = ex, ey
            else:
                for j in range(0, len(args), 7):
                    rx, ry = args[j], args[j + 1]
                    rotation = args[j + 2]
                    large_arc = int(args[j + 3])
                    sweep = int(args[j + 4])
                    ex, ey = x + args[j + 5], y + args[j + 6]
                    result_parts.append(
                        f"A{rx:.2f} {ry:.2f} {rotation:.2f} {large_arc} {sweep} {ex:.2f} {ey:.2f}"
                    )
                    x, y = ex, ey
            last_control = None

        elif cmd == 'T':
            # Smooth quadratic - pass through (would need tracking)
            for j in range(0, len(args), 2):
                x, y = args[j], args[j + 1]
                result_parts.append(f"L{x:.2f} {y:.2f}")
            last_control = None

        elif cmd == 't':
            for j in range(0, len(args), 2):
                x += args[j]
                y += args[j + 1]
                result_parts.append(f"L{x:.2f} {y:.2f}")
            last_control = None

    return " ".join(result_parts)


def straighten_svg_file(input_path, output_path, tolerance=1.0):
    """
    Smart straighten all paths in an SVG file.
    Converts nearly-straight Bezier curves to lines while preserving actual curves.

    Args:
        input_path: Path to input SVG file
        output_path: Path for output SVG file
        tolerance: Maximum control point deviation to consider straight (in SVG units)

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        with open(input_path, 'r') as f:
            svg_content = f.read()

        path_pattern = re.compile(r'(<path[^>]*\sd=")([^"]+)("[^>]*>)', re.IGNORECASE)

        def replace_path(match):
            prefix = match.group(1)
            d = match.group(2)
            suffix = match.group(3)
            straightened_d = straighten_svg_path(d, tolerance)
            return prefix + straightened_d + suffix

        optimized_svg = path_pattern.sub(replace_path, svg_content)

        with open(output_path, 'w') as f:
            f.write(optimized_svg)

        return True, "Success"

    except Exception as e:
        return False, str(e)
