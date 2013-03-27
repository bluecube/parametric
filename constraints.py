class Constraint:
    def __init__(self, primitives, constants):
        self.primitives = primitives
        self.constants = constants

    def update(self):
        """ Called at least every time a structure of the scene (not variable
        values) changes.  At that point only arguments passed in constructor
        remain valid and all other cached values must be recalculated.
        Variable values may change any time. """
        raise NotImplementedError()

    def get_error(self):
        """ Return the current error of this constraint (based on values of
        variables in the linked primitives).

        The error must be positive!"""
        raise NotImplementedError()

    def get_error_pds(self):
        """ Return a dictionary of partial derivative of the error wrt. all
        relevant variables."""
        raise NotImplementedError()


#class EqualLength(Constraint):
#    def __init__(self, *primitives):
#        super().__init__(*primitives)
#
#    def get_error(self):
#        pass


class FixedLength(Constraint):
    CONSTANT_NAMES = "l"

    def update(self):
        length = self.constants[0]
        self._l2 = length * length
        line = self.primitives[0]
        self._p1 = line.variables[0]
        self._p2 = line.variables[1]

    def get_error(self):
        x = self._p1.x.value - self._p2.x.value
        y = self._p1.y.value - self._p2.y.value

        # (x1 - x2)^2 + (y1 - y2)^2 - length^2
        # x1^2 - 2 * x1 * x2 + x2^2 + y1^2 - 2 * y1 * y2 + y2^2 - length^2

        return x * x + y * y - self._l2

    def get_error_pds(self):
        return {
            self._p1.x: 2 * (self._p1.x.value - self._p2.x.value),
            self._p1.y: 2 * (self._p1.y.value - self._p2.y.value),
            self._p2.x: 2 * (self._p2.x.value - self._p1.x.value),
            self._p2.y: 2 * (self._p2.y.value - self._p1.y.value)
            }

#class EqualRadius(Constraint):
#    def __init__(self, *primitives):
#        super().__init__(*primitives):
#
#class FixedRadius(Constraint):
#    def __init__(self, arc, radius):
#        super().__init__(arc):
#        self.radius = radius
