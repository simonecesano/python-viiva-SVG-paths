# Viita - a Python vector path library

## Name

Viiva means line in finnish. It also sounds like an enthusiastic uttering of "Hooray" in Italian. A lucky coincidence.

## Purpose and reason

The goal is to provide a library to work with SVG paths that encapsulates the best of Andre Port's [svgpathtools](https://github.com/mathandy/svgpathtools)
and Simon Cozens' [beziers.py](https://github.com/simoncozens/beziers.py), while providing a few additional benefits:

- a unified and more tolerant interface (2-item tuples, objects with x and y attributes, and imaginary numbers) as inputs
- parsing of d-attributes and of SVG elements
- a preference for immutability in methods 
- snake-case whenever possible
- an attempt (not sure if I succeded) at being more consistent in methods
- some additional path-base functionality
- easy conversion to Shapely polygon/polyline objects

The reason for that - if it isn't obvious - is that while some functionality overlaps, some is available in only one library, for example:

- parsing and conversion from SVG elements is only in svgpathtools
- offsetting and boolean ops are only available in beziers.py

and I found myself more and more in need of both.

## Caveats and bugs

This is work in progress, and will contain bugs. 

## License

Copyright (c) 2024 Simone Cesano

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Documentation

### Initialization and logic

Paths can be initialized from segments

    [code]

Segments can in turn be initalized from imaginary numbers, like for svgpathtools

    [code]

provided as keyword arguments as above, or as argslist

    [code]

or also from 2-item tuples:

    [code]

or from items that have an x and a y property 

    [code]

Paths can also be initialized from parsing d attributes:

    [code]

or from elements

    [code]

which - in case of rects, elllipses, circles, polygons and polylines - get converted automatically:

    [code]

### SVG path functionality

This class inherits all methods from svgpathtools' Path class:

- [ list goes here ]

modifying the following

- [ list goes here ]

and providing a few additional ones:

- [ list goes here ]


### Bezier path functionality

The Path class provides a .to_beziers() method that converts a mixed-segments path to a strict-cubic-beziers BezierPath
that inherits all methods from Simon Cozens [BezierPath](https://simoncozens.github.io/beziers.py/source/beziers.path.html)
mapping them from camel-case to snake-case like this:

- [ list goes here ]

modifying the following

- [ list goes here ]

and providing a few additional ones:

- [ list goes here ]
