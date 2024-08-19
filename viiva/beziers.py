import re
import sys

from beziers.path import BezierPath as CBezierPath
from beziers.point import Point as CPoint
from beziers.cubicbezier import CubicBezier as CCubicBezier
from beziers.quadraticbezier import QuadraticBezier as CQuadraticBezier
from beziers.line import Line as CLine

from .paths import *

# from . paths 

# ------------------------------------------------------------------------------
# utility for point conversion
# ------------------------------------------------------------------------------

def _i2p(i): return CPoint(i.real, i.imag)

def _p2i(p): return complex(p.x, p.y)

# ------------------------------------------------------------------------------
# decorator for camelcase functions
# ------------------------------------------------------------------------------

from functools import wraps

def snake_to_camel(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.capitalize() for x in components[1:])

def camel_to_snake(camel_str):
    # Insert an underscore before each uppercase letter (that isn't the first letter) and convert to lowercase
    snake_str = re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()
    return snake_str

def ensure_subclass_instance(obj, cls):
    """Ensure that the object is an instance of the subclass."""
    if isinstance(obj, cls.__bases__[0]):  # Assuming a single direct superclass
        obj.__class__ = globals().get(obj.__class__.__name__, obj.__class__)
    return obj

def method_wrapper(method_name, cls):
    """Wrap a method to ensure the result is an instance of the subclass."""
    original_method = getattr(cls, method_name)

    @wraps(original_method)
    def wrapper(self, *args, **kwargs):
        result = original_method(self, *args, **kwargs)
        
        # Ensure the result is an instance of the subclass
        if isinstance(result, list):
            return [ensure_subclass_instance(item, cls) for item in result]
        else:
            return ensure_subclass_instance(result, cls)

    return wrapper

def map_methods_to_snake_case(cls):
    """Decorator to wrap all methods to ensure subclass instance returns."""
    # Get all methods from the superclass
    for method_name in dir(cls.__bases__[0]):
        if not method_name.startswith("_"):  # Skip private methods and dunder methods
            # Map the method name to snake_case
            snake_name = camel_to_snake(method_name)
            # Apply wrapper to camelCase methods
            setattr(cls, method_name, method_wrapper(method_name, cls))
            # Apply wrapper to snake_case methods (only if it's not already defined)
            if snake_name != method_name and snake_name not in dir(cls):
                setattr(cls, snake_name, method_wrapper(method_name, cls))
    return cls

# ------------------------------------------------------------------------------

@map_methods_to_snake_case
class BezierPath(CBezierPath):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)
        
    @classmethod
    def from_segments(_, segments): return super().fromSegments(segments)
    
    @classmethod
    def from_path(_, path):
        # print(path, file=sys.stderr)
        u = []
        for s in path:
            l = [ _i2p(i) for i in list(s) ]
            if isinstance(s, CubicBezier):
                u.append(CCubicBezier(*l))
            elif isinstance(s, Line):
                u.append(CLine(*l))
        b = BezierPath.from_segments(u)
        return b

    def to_path(self):
        segments = self.asSegments()
        # print(segments)
        for i, s in enumerate(segments):
            n = "" + s.__class__.__name__
            b = globals()[n](*[ _p2i(p) for p in list(s) ])
            # print(n)
            # print([ _p2i(p) for p in list(s) ])
            # print(globals()[n])
            # print(b)
            segments[i] = b
        return Path(*segments)
        
    
    def division(self, other):
        # intersect + subtract
        # total area is unchanged
        raise NotImplementedError

    def fracture(self, other):
        # intersect and subtract two-ways
        # total area stays same
        raise NotImplementedError

    def dash(self):
        # messes up in sampling
        raise NotImplementedError

    def smoothed(self, *args, **kwargs):
        _self = copy.deepcopy(self)
        return _self.smooth(*args, **kwargs)
    
    def d(self):
        d = self.asSVGPath()
        if self[0][0] != self[-1][-1]:
            d = re.sub(r'\s*z\s*$', '', d, flags=re.IGNORECASE)
        return(d)
    
    def __getitem__(self, item):
        i = self.asSegments()[item]
        n = i.__class__.__name__
        b = globals()[n](*[ _p2i(p) for p in list(i) ])
        return b

    def __len__(self):
        return len(self.asSegments())
    
    def __getattr__(self, name):
        # print(name, file=sys.stderr)
        # Check if the attribute or method exists in Path
        if hasattr(Path, name):
            # If it does, get the method from Path
            def method(*args, **kwargs):
                # Convert the BezierPath to a Path and call the method
                path_obj = self.to_path()
                return getattr(path_obj, name)(*args, **kwargs)
            return method
        else:
            # If it doesn't exist in Path, raise an AttributeError
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        # return lambda *args, **kvargs: None
