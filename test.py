#!/usr/bin/python

import scene
import primitives
import expressions
import constraints
import properties

import math

s = scene.Scene()

def v(x, *args, **kwargs):
    return expressions.Variable(x, *args, **kwargs)

a = primitives.Point(v(0, 'ax'), v(2, 'ay'))
b = primitives.Point(v(1, 'bx'), v(0, 'by'))
c = primitives.Point(v(3, 'cx'), v(3, 'cy'))

l1 = primitives.LineSegment(a, b)
l2 = primitives.LineSegment(b, c)
l3 = primitives.LineSegment(c, a)

s.add_primitive(l1)
s.add_primitive(l2)
s.add_primitive(l3)

s.add_constraint(constraints.equal(l1.length, 2))
s.add_constraint(constraints.equal(l3.length, 3))
s.add_constraint(constraints.equal(properties.angle(l1, l3), math.radians(-30)))
s.add_constraint(constraints.horizontal(l1))

s.solve()

with open("/tmp/test.svg", "w") as fp:
    s.export_svg(fp, 100)

