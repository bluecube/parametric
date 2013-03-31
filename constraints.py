import expressions

def equal(a, b):
    return _Equal(a, b)

def vertical(line):
    return _Equal(line.p1.x, line.p2.x)

def horizontal(line):
    return _Equal(line.p1.y, line.p2.y)

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

    def __str__(self):
        raise NotImplementedError()

class _Equal(Constraint):
    def __init__(self, a, b):
        self._a = a
        self._b = b
        self._expr = expressions.sub(a, b)

    def get_error(self):
        return self._expr.get_value()

    def get_error_pds(self):
        return self._expr.get_pds()

    def __str__(self):
        return str(self._a) + " = " + str(self._b)


#class EqualRadius(Constraint):
#    def __init__(self, *primitives):
#        super().__init__(*primitives):
#
#class FixedRadius(Constraint):
#    def __init__(self, arc, radius):
#        super().__init__(arc):
#        self.radius = radius
