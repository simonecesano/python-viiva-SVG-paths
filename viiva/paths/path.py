import copy
import svgpathtools

from math import sqrt

import shapely.geometry as geom

from .. import beziers

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
