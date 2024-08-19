import copy
import svgpathtools

from math import sqrt

import shapely.geometry as geom

from . import beziers

# ------------------------------------------------------------------------

def to_complex(point):
    """
    Convert a point to a complex number.
    """
    if isinstance(point, (tuple, list)) and len(point) == 2:
        return complex(point[0], point[1])
    elif hasattr(point, 'x') and hasattr(point, 'y'):
        return complex(point.x() if callable(point.x) else point.x,
                       point.y() if callable(point.y) else point.y)
    elif isinstance(point, dict) and 'x' in point and 'y' in point:
        return complex(point['x'], point['y'])
    return point  # Return as is if it's not a recognized point format

def preprocess(args):
    """
    Preprocess args or kwargs to convert any recognized point format to complex numbers.
    
    Args:
        args: A list, tuple, or dictionary of arguments.
    
    Returns:
        A new list, tuple, or dictionary with points converted to complex numbers.
    """
    if isinstance(args, (list, tuple)):
        return type(args)(to_complex(arg) if isinstance(arg, (list, tuple, dict)) or hasattr(arg, 'x') else arg for arg in args)
    elif isinstance(args, dict):
        return {k: to_complex(v) if isinstance(v, (list, tuple, dict)) or hasattr(v, 'x') else v for k, v in args.items()}
    return args

class TolerantPath:
    def __init__(self, *args, **kwargs):
        # Preprocess args and kwargs to convert points to complex numbers
        args   = preprocess(args)
        kwargs = preprocess(kwargs)
        # Call the next class in the MRO (Method Resolution Order)
        super().__init__(*args, **kwargs)

    def to_shapely():
        return Path(self).to_shapely()

    def to_beziers():
        return Path(self).to_beziers()

    def d(self):
        if self.isclosed():
            return Path(self).d() + " Z"
        else:
            return Path(self).d()

        
# ------------------------------------------------------------------------

class Arc(TolerantPath, svgpathtools.Arc):
    def approximate_with_cubics(self):
        path = Path(self)
        path.approximate_arcs_with_cubics()
        for i, p in enumerate(path):
            p.__class__ = globals().get(p.__class__.__name__)
        return path

class Line(TolerantPath, svgpathtools.Line):
    def to_cubic_old(self):
        start = self.start
        end = self.end
        cubic_bezier = CubicBezier(start, start, end, end)
        return cubic_bezier

    def to_cubic(self, t=1/3):
        """
        Convert a line segment to a cubic Bezier curve with control points
        positioned symmetrically at a parametric distance `t` from the start and end.

        Parameters:
        -----------
        t : float, optional
            A value between 0 and 1 that determines the relative position of the control points
            along the line segment. Default is 1/3.

        Returns:
        --------
        CubicBezier
            The corresponding cubic Bezier curve.
        """
        start = self.start
        end = self.end

        # Ensure t is between 0 and 1
        if not (0 <= t <= 1):
            raise ValueError("Parameter t must be between 0 and 1.")

        # Calculate the control points at a parametric distance t from the start and end
        control1 = start + t * (end - start)
        control2 = start + (1 - t) * (end - start)

        # Create the CubicBezier curve with the calculated control points
        cubic_bezier = CubicBezier(start, control1, control2, end)
        return cubic_bezier
    
class CubicBezier(TolerantPath, svgpathtools.CubicBezier):
    def as_polyline(self, flatness=0.01):
        """
        Recursively flatten a Bézier curve into a polyline with a given flatness.

        Args:
            bezier: An svgpathtools CubicBezier or QuadraticBezier object.
            flatness: The maximum allowable deviation between the Bézier curve and the polyline.

        Returns:
            Path: A path representing the polyline.
        """

        def subdivide(bez, depth=0, max_recursion=10):
            """Recursively subdivide the Bézier curve until flatness criterion is met."""
            p0, p1, p2, p3 = bez.start, bez.control1, bez.control2, bez.end
            max_dist = max(
                (abs((p2.real - p0.real) * (p0.imag - p1.imag) - (p2.imag - p0.imag) * (p0.real - p1.real)) / sqrt((p2.real - p0.real)**2 + (p2.imag - p0.imag)**2)),
                (abs((p3.real - p1.real) * (p1.imag - p2.imag) - (p3.imag - p1.imag) * (p1.real - p2.real)) / sqrt((p3.real - p1.real)**2 + (p3.imag - p1.imag)**2))
            )

            if max_dist > flatness and depth < max_recursion:  # Limit depth to avoid infinite recursion
                one, two = bez.split(0.5)
                return subdivide(one, depth + 1)[:-1] + subdivide(two, depth + 1)
            else:
                return [p0, p3]

        points = subdivide(self)
        polyline_path = Path()
        for i in range(len(points) - 1):
            polyline_path.append(Line(points[i], points[i + 1]))
        return polyline_path

class QuadraticBezier(TolerantPath, svgpathtools.QuadraticBezier):
    def to_cubic(self):
        P0 = self.start
        P1 = self.control
        P2 = self.end

        # Calculate the control points for the cubic Bézier curve
        C0 = P0
        C1 = P0 + 2/3 * (P1 - P0)
        C2 = P2 + 2/3 * (P1 - P2)
        C3 = P2

        # Return a new instance of svgpathtools.CubicBezier
        return CubicBezier(C0, C1, C2, C3)    

class Path(svgpathtools.Path):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], str):
            parsed_path = svgpathtools.parse_path(args[0])
            for i, segment in enumerate(parsed_path):
                segment.__class__ = globals().get(segment.__class__.__name__)
                parsed_path[i] = segment
            super().__init__(*parsed_path)
        else:
            super().__init__(*args, **kwargs)


    def kinks(self, tol=1e-8):
        return svgpathtools.kinks(self, tol)

    def smoothed(self, maxjointsize=3, tightness=1.99, ignore_unfixable_kinks=False):
        path = self.to_cubics()
        path = svgpathtools.smoothed_path(path, maxjointsize, tightness, ignore_unfixable_kinks)
        for i, segment in enumerate(path):
            segment.__class__ = globals().get(segment.__class__.__name__)
            path[i] = segment
        path.__class__ = globals().get(path.__class__.__name__)
        return path

            
    def to_cubics(self, error=0.1):
        _self = copy.deepcopy(self)
        _self.approximate_arcs_with_cubics(error=error)
        for i, a in enumerate(_self):
            if isinstance(a, Line):
                _self[i] = a.to_cubic()
            else:
                a.__class__ = globals().get(a.__class__.__name__)
                _self[i] = a
        return _self

    def as_polyline(self, flatness=0.1):
        """
        Convert an svgpathtools Path to a polyline Path using Inkscape-like flattening with specified flatness.

        Args:
            path (Path): An svgpathtools Path object.
            flatness (float): The maximum allowable deviation between the polyline and the original path.

        Returns:
            Path: A new svgpathtools Path object composed of Line segments approximating the original path.
        """

        if all(isinstance(segment, Line) for segment in self):
            return self
        
        path = self.to_cubics()
        polyline_path = Path()

        for segment in path:
            if isinstance(segment, CubicBezier):
                lines = segment.as_polyline(flatness)
                for line in lines:
                    polyline_path.append(line)
            elif isinstance(segment, Line):
                polyline_path.append(Line(segment.start, segment.end))
            elif isinstance(segment, Arc):
                arc_points = segment.approximate_with_cubics()  # Approximate Arc with Cubic Beziers
                for bez in arc_points:
                    points = bez.as_polyline(flatness)
                    for i in range(len(points) - 1):
                        polyline_path.append(Line(points[i], points[i + 1]))
        return polyline_path

    def to_beziers(self):
        return beziers.BezierPath.from_path(self.to_cubics())
        
    def to_shapely(self):
        """
        Convert an svgpathtools.Path object composed of Line segments
        into a corresponding Shapely geometry object.

        Args:
            path (svgpathtools.Path): The input path consisting of Line segments.

        Returns:
            shapely.geometry.LineString or shapely.geometry.Polygon: The corresponding Shapely object.
        """
        path = self.as_polyline()

        # Extract the coordinates from the Line segments
        coords = [(line.start.real, line.start.imag) for line in path if isinstance(line, Line)]
        if not coords:
            raise ValueError("Path does not contain any Line segments.")

        # Close the path if the first and last coordinates are the same
        if coords[0] == coords[-1]:
            return geom.Polygon(coords)
        else:
            return geom.LineString(coords)

    def d(self):
        if self.isclosed():
            return super().d() + " Z"
        else:
            return super().d()
        
    
# ------------------------------------------------------------------------
# x add to_cubic to Line
# x add approximate_with_cubics to Arc
# - cleanup as_polyline (add Quadratic case, fix Arc case)
# x change as_ with to_
# x change as_beziers in to_cubics
# - create a bunch of test paths and test against them
# x create to_shapely function
# x move as_beziers in to_beziers to actually convert to cozens' beziers
# - ensure that error param is passed on in approximation
# - check that to_cubics actually closes the path
# ------------------------------------------------------------------------

# I'd like to have the following project structure

# - viiva/__init__py - the main package
# - viiva/paths.py contains CubicBezier, Arc, Line, QuadraticBezier classes
# - viiva/paths/path.py contains the Path class
# - viiva/beziers.py contains the BezierPath class

# with the following requirements

# - the Path class and the BezierPath class are both used inside viiva/paths.py
# - inside viiva/paths.py a few functions are defined that are used inside viiva/paths/path.py
# - I'd like to be able to write "from viiva import *" and have CubicBezier, Arc, Line, QuadraticBezier, Path and BezierPath classes available - and nothing else

# Here are a few questions

# - how must the imports look like in each file
# - how does viiva/__init__.py look like


