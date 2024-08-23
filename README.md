# Viita - a Python vector path library

## Name

Viiva means line in finnish. It also sounds like an enthusiastic uttering if "Hooray" in Italian.

## Purpose and reason

The goal is to provide a library to work with SVG paths that encapsulates the best of Andre Port's [svgpathtools](https://github.com/mathandy/svgpathtools)
and Simon Cozens' [beziers.py](https://github.com/simoncozens/beziers.py), while providing a few additional benefits:

- a unified and more tolerant interface (2-item tuples, objects with x and y attributes, and imaginary numbers) as inputs
- parsing of d-attributes and of SVG elements
- a preference for immutability in methods 
- snake-case whenever possible
- an attempt (not sure if I succeded) at being more consistent in methods
- some added functionality

The reason for that - if it isn't obvious - is that while some functionality overlaps, some is available in only one library, for example:

- parsing and conversion from SVG elements is only in svgpathtools
- offsetting and boolean ops are only available in beziers.py

and I found myself more and more in need of both.

## Caveats and bugs

This is work in progress, and will contain bugs. 

## License

This module is under a MIT License.

## Documentation

WIP
