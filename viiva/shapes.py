import svgpathtools
from . import paths

class Shape:
    def __str__(self):
        return str(self.__dict__)

    def element(self):
        pass
    @property    
    def type(self):
        return self.__class__.__name__

    @property    
    def d(self):
        shape_def = {key: value for key, value in self.__dict__.items() if value is not None}
        return getattr(svgpathtools.svg_to_paths, self.tag + "2pathd")(shape_def)

    def as_path(self):
        return paths.Path(self.d)

    def __getattr__(self, name):
        # Check if the method exists in the parent class (svgpathtools.Path)
        if hasattr(paths.Path, name):
            return getattr(self.as_path(), name)
        raise AttributeError(f"Method '{name}' not found.")
    
class Rect(Shape):
    def __init__(self, x=0, y=0, width=0, height=0, rx=None, ry=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rx = rx
        self.ry = ry
        self.tag = "rect"
    
class Circle(Shape):
    def __init__(self, cx=0, cy=0, r=0):
        self.cx = cx
        self.cy = cy
        self.r = r
        self.tag = "circle"

    @property
    def d(self):
        shape_def = {key: value for key, value in self.__dict__.items() if value is not None}
        return getattr(svgpathtools.svg_to_paths, "ellipse" + "2pathd")(shape_def)

class Ellipse(Shape):
    def __init__(self, cx=0, cy=0, rx=0, ry=0):
        self.cx = cx
        self.cy = cy
        self.rx = rx
        self.ry = ry
        self.tag = "ellipse"



class Line(Shape):
    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.tag = "line"

class Polyline(Shape):
    def __init__(self, points=None):
        if points is None:
            points = []
        self.points = points
        self.tag = "polyline"


class Polygon(Shape):
    def __init__(self, points=None):
        if points is None:
            points = []
        self.points = points
        self.tag = "polygon"
