import copy
import svgpathtools
from math import sqrt

import xml.etree.ElementTree as ET
import shapely.geometry as geom

# from . import beziers

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

