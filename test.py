import parametric

angle = 15
thickness = 5

s = parametric.Solver()

a = parametric.Point(0, 0, fixed=True, name="a")
b = parametric.Point(0, -thickness, name="b")
c = parametric.Point(-thickness, -thickness, name="c")
d = parametric.Point(-thickness, 0, name="d")

la = parametric.LineSegment(a, b)
lb = parametric.LineSegment(b, c)
lc = parametric.LineSegment(c, d)
ld = parametric.LineSegment(d, a)

s.add_constraint(parametric.Angle(la, -90 - angle))
s.add_constraint(parametric.Perpendicular(la, lb))
s.add_constraint(parametric.Length(lb, thickness))
s.add_constraint(parametric.Perpendicular(lc, ld))
s.add_constraint(parametric.Length(lc, thickness))
s.add_constraint(parametric.Horizontal(ld.a, ld.b))

s._print_internal_state()
