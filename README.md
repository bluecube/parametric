# parametric

This is a very experimental library for parametric modelling in 2D (but extension to 3D would be easy).
Parametric allows you to define objects (points, lines, ...) and set constraints on their properties (perpendicular, length, ...).

Heavy lifting is provided by constrained optimization functions from SciPy, using gradients computed by autograd.

Parametric is designed to work with CodeCAD, but there is no dependency between them.
End goal is to have a graphical constraint solver (like SolidWorks or Fusion360 have) powered by this library.

The code is incomplete, API is uncomfortable and a lot more testing is needed (both automated and manual). But it works :-)
