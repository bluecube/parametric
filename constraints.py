import expressions

class Constraint:
    def get_error(self):
        """ Return the current error of this constraint (based on values of
        expressions in the linked primitives).

        The error must be positive!"""
        raise NotImplementedError()

    def get_error_pds(self):
        """ Return a dictionary of partial derivative of the error wrt. all
        relevant variables."""
        raise NotImplementedError()


class Equal(Constraint):
    def __init__(self, a, b):
        self._expr = expressions.sub(a, b)

    def get_error(self):
        return self._expr.get_value()

    def get_error_pds(self):
        return self._expr.get_pds()


class Vertical(Constraint):
    def __init__(self, line):
        self._x1 = line.p1.x
        self._x2 = line.p2.x

    def get_error(self):
        return self._x1.get_value() - self._x2.get_value()

    def get_error_pds(self):
        return {
            self._x1: 1,
            self._x2: -1
            }

class Horizontal(Constraint):
    def __init__(self, line):
        self._y1 = line.p1.y
        self._y2 = line.p2.y

    def get_error(self):
        return self._y1.get_value() - self._y2.get_value()

    def get_error_pds(self):
        return {
            self._y1: 1,
            self._y2: -1
            }

#class EqualRadius(Constraint):
#    def __init__(self, *primitives):
#        super().__init__(*primitives):
#
#class FixedRadius(Constraint):
#    def __init__(self, arc, radius):
#        super().__init__(arc):
#        self.radius = radius
