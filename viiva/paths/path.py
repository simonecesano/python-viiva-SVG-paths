from ..paths import *
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


    @classmethod
    def parse_d(classe, d):
        """
        Parse an SVG path data string into path segments

        Args:
            d (str): The SVG path data string to be parsed.

        Returns:
            Path: An object representing the parsed path with segments whose classes 
            have been updated to be globally recognized.
        """
        parsed_path = svgpathtools.parse_path(d)
        for i, segment in enumerate(parsed_path):
            segment.__class__ = globals().get(segment.__class__.__name__)
            parsed_path[i] = segment
        parsed_path.__class__ = globals().get(parsed_path.__class__.__name__)
        return parsed_path
    
    @classmethod
    def parse_element(classe, element):
        """
        Parse an SVG element string into a path object.

        Args:
            element (str): The SVG element string to be parsed. This should be an XML string 
                           representing an SVG element such as a circle or path.

        Returns:
            Path: An object representing the path created from the parsed SVG element.
        """

        root = ET.fromstring(element)
        if root.tag == "circle":
            attrib = root.attrib
            t = getattr(svgpathtools.svg_to_paths, "ellipse2pathd")
            attrib["rx"] = attrib["ry"] = attrib["r"]
            return Path(t(attrib))
        elif root.tag == "path":
            return classe.parse_d(root.attrib["d"])
        else:
            t = getattr(svgpathtools.svg_to_paths, root.tag + "2pathd")
            return Path(t(root.attrib))

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
        """
        Convert all path segments in the current object to cubic Bezier curves.
 
        Args:
            error (float, optional): The maximum error tolerance for approximating arcs with cubic Bezier curves.
                                     A smaller value results in a closer approximation with more cubic segments.
                                     Default is 0.1.

        Returns:
            The modified copy of the current object with all segments converted to cubic Bezier curves.
        """

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
        
    
