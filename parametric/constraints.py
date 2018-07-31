import numpy


class _Constraint:
    @classmethod
    def evaluate(cls, variable_values, parameters):
        """ Calculate error terms for each of the constraints in parameters.
        variable_values is a numpy array, parameters is a numpy record array with
        dtype matching `get_parameters()` return value. Variable instances in
        parameter arrays have integral type and are valid indices into variable_values,
        numerical parameters have floating point type. """
        raise NotImplementedError()

    def get_parametrers(self):
        """ Return an iterable of tuples (parameter_name, parameter_value).
        Parameter values can either be variable instances, or numbers.
        All instances of this class must return identical keys and identical
        variable/number types. """
        raise NotImplementedError()


class VariableFixed(_Constraint):
    """ Variable is fixed to the current value of the variables.
    This constraint is special in that it is auto generated for every variable and
    used as a soft constraint. """

    def __init__(self, variable):
        self.variable = variable

    def get_parameters(self):
        return [("variable", self.variable), ("value", self.variable.value)]


class Angle(_Constraint):
    """ Line absolute angle """

    def __init__(self, line, angle):
        self.line = line
        self.angle = angle

    def get_parameters(self):
        return [
            ("ax", self.line.a.x),
            ("ay", self.line.a.y),
            ("bx", self.line.b.x),
            ("by", self.line.b.y),
            ("angle", self.angle),
        ]


class Perpendicular(_Constraint):
    def __init__(self, line1, line2):
        self.line1 = line1
        self.line2 = line2

    def get_parameters(self):
        return [
            ("ax1", self.line1.a.x),
            ("ay1", self.line1.a.y),
            ("bx1", self.line1.b.x),
            ("by1", self.line1.b.y),
            ("ax2", self.line2.a.x),
            ("ay2", self.line2.a.y),
            ("bx2", self.line2.b.x),
            ("by2", self.line2.b.y),
        ]


class Length(_Constraint):
    def __init__(self, line, length):
        self.line = line
        self.length = length

    def get_parameters(self):
        return [
            ("ax", self.line.a.x),
            ("ay", self.line.a.y),
            ("bx", self.line.b.x),
            ("by", self.line.b.y),
            ("length", self.length),
        ]


class VariablesEqual(_Constraint):
    def __init__(self, variable1, variable2):
        self.variable1 = variable1
        self.variable2 = variable2

    def get_parameters(self):
        return [("v1", self.variable1), ("v2", self.variable2)]


class Vertical(VariablesEqual):
    def __init__(self, point1, point2):
        super().__init__(point1.x, point2.x)
        self.point1 = point1
        self.point2 = point2


class Horizontal(VariablesEqual):
    def __init__(self, point1, point2):
        super().__init__(point1.y, point2.y)
        self.point1 = point1
        self.point2 = point2
