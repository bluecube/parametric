#!/usr/bin/python

import scene
import primitives
import expressions
import constraints
import properties

import math

s = scene.Scene()

def v(x):
    return expressions.Variable(x)

a = primitives.Point(v(0), v(2))
b = primitives.Point(v(1), v(0))
c = primitives.Point(v(3), v(3))

l1 = primitives.LineSegment(a, b)
l2 = primitives.LineSegment(b, c)
l3 = primitives.LineSegment(c, a)

s.add_primitive(l1)
s.add_primitive(l2)
s.add_primitive(l3)

s.add_constraint(constraints.Equal(l1.length, 2))
s.add_constraint(constraints.Equal(l3.length, 3))
s.add_constraint(constraints.Equal(properties.angle(l1, l3), math.radians(30)))
s.add_constraint(constraints.Horizontal(l1))

s.solve()

with open("/tmp/test.svg", "w") as fp:
    s.export_svg(fp, 100)

