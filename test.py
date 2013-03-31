#!/usr/bin/python

import scene
import primitives
import constraints
import properties

import math

s = scene.Scene()

a = primitives.Point.fresh_variables(0, 2, 'A')
b = primitives.Point.fresh_variables(1, 0, 'B')
c = primitives.Point.fresh_variables(3, 3, 'C')

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

