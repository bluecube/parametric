import drawables
import expressions

class Primitive(drawables.Drawable):
    def __init__(self, subobjects, own_expressions):
        self.subobjects = subobjects
        self.expressions = set(own_expressions)

        for obj in self.subobjects:
            self.expressions.update(obj.expressions)

    def export_svg(self, fp, scale):
        """ Draw subobjects to svg. To be called as super().export_svg(...) """
        for obj in self.subobjects:
            obj.export_svg(fp, scale)


class Point(Primitive):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        super(Point, self).__init__([], [self.x, self.y])

    def export_svg(self, fp, scale):
        x = float(self.x) * scale
        y = float(self.y) * scale
        w = 5

        fp.write('<rect x="{}" y="{}" width="{}" height="{}" class="cp" />\n'.format(
            x - w, y - w, 2 * w, 2 * w))
        super(Point, self).export_svg(fp, scale)


class LineSegment(Primitive):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

        vx = expressions.sub(p1.x, p2.x)
        vy = expressions.sub(p1.y, p2.y)
        self.length = expressions.sqrt(expressions.dot_product(vx, vy, vx, vy))

        super(LineSegment, self).__init__([p1, p2], [])

    def export_svg(self, fp, scale):
        fp.write('<line x1="{}" y1="{}" x2="{}" y2="{}" class="primitives" />\n'.format(
            float(self.p1.x) * scale, float(self.p1.y) * scale,
            float(self.p2.x) * scale, float(self.p2.y) * scale))
        super(LineSegment, self).export_svg(fp, scale)


#class Circle(Primitive):
#    def __init__(self, center, radius):
#        pass
#
#class ThreePointArc(Primitive):
#    def __init__(self, p1, p2, p3):
#        super().__init__(p1 = p1, p2 = p2, p3)

