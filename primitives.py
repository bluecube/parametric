import drawables
import variables

class Primitive(drawables.Drawable):
    def __init__(self, subobjects, own_variables):
        self.subobjects = subobjects
        self.variables = set(own_variables)

        for obj in self.subobjects:
            self.variables.update(obj.variables)

    def export_svg(self, fp, scale):
        """ Draw subobjects to svg. To be called as super().export_svg(...) """
        for obj in self.subobjects:
            obj.export_svg(fp, scale)


class Point(Primitive):
    def __init__(self, x, y):
        self.x = variables.var(x)
        self.y = variables.var(y)
        super(Point, self).__init__([], [self.x, self.y])

    def export_svg(self, fp, scale):
        x = self.x.value * scale
        y = self.y.value * scale
        w = 5

        fp.write('<rect x="{}" y="{}" width="{}" height="{}" class="cp" />\n'.format(
            x - w, y - w, 2 * w, 2 * w))
        super(Point, self).export_svg(fp, scale)


class LineSegment(Primitive):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        super(LineSegment, self).__init__([p1, p2], [])

    def export_svg(self, fp, scale):
        fp.write('<line x1="{}" y1="{}" x2="{}" y2="{}" class="primitives" />\n'.format(
            self.p1.x.value * scale, self.p1.y.value * scale,
            self.p2.x.value * scale, self.p2.y.value * scale))
        super(LineSegment, self).export_svg(fp, scale)


#class Circle(Primitive):
#    def __init__(self, center, radius):
#        pass
#
#class ThreePointArc(Primitive):
#    def __init__(self, p1, p2, p3):
#        super().__init__(p1 = p1, p2 = p2, p3)

