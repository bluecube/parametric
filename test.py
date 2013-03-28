#!/usr/bin/python

import scene
import primitives
import variables
import constraints

s = scene.Scene()

a = primitives.Point(0, 2)
b = primitives.Point(1, 0)
c = primitives.Point(3, 3)

l1 = primitives.LineSegment(a, b)
l2 = primitives.LineSegment(b, c)
l3 = primitives.LineSegment(c, a)

c1 = constraints.FixedLength([l1], [2])
c2 = constraints.FixedLength([l2], [3])
c3 = constraints.FixedLength([l3], [2])
c4 = constraints.Horizontal([l3])

s.add_primitive(l1)
s.add_primitive(l2)
s.add_primitive(l3)

s.add_constraint(c1)
s.add_constraint(c2)
s.add_constraint(c3)
s.add_constraint(c4)

s.solve()

with open("/tmp/test.svg", "w") as fp:
    s.export_svg(fp, 100)

