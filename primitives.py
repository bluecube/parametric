import drawables
import variables

class Primitive(drawables.Drawable):
    def __init__(self, *variables):
        self.variables = variables

#        for i, name in enumerate(self.VARIABLE_NAMES):
#            def getter(self2):
#                return self2.variables[i]
#            def setter(self2, value):
#                self2.variables[i] = value
#            prop = property(getter, setter)
#            setattr(self.__class__, name, prop)

    def export_svg(self, fp, scale):
        """ Draw control points to svg. To be called as super().export_svg(...) """
        for var in self.variables:
            if isinstance(var, variables.ControlPoint2D):
                var.export_svg(fp, scale)

#class Point(Primitive):
#    def __init__(self, p):
#        Primitive.__init__(self, p = p)


class LineSegment(Primitive):
#    VARIABLE_NAMES = ["p1", "p2"]

    def export_svg(self, fp, scale):
        fp.write('<line x1="{}" y1="{}" x2="{}" y2="{}" class="primitives" />\n'.format(
            self.variables[0].x.value * scale, self.variables[0].y.value * scale,
            self.variables[1].x.value * scale, self.variables[1].y.value * scale))
        super(LineSegment, self).export_svg(fp, scale)

#class Circle(Primitive):
#    def __init__(self, center, radius):
#        pass
#
#class ThreePointArc(Primitive):
#    def __init__(self, p1, p2, p3):
#        super().__init__(p1 = p1, p2 = p2, p3)

