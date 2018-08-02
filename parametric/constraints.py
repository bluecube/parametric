import math

import numpy


class _Constraint:
    @staticmethod
    def evaluate(variable_values, parameters, output):
        """ Calculate error terms for each of the constraints in parameters.
        variable_values is a numpy array, parameters is a numpy record array with
        dtype matching `get_parameters()` return value. Variable instances in
        parameter arrays have integral type and are valid indices into variable_values,
        numerical parameters have floating point type.

        Output should be directly written into the output array (either like
        `numpy.someop(somearg, out=output)`, or `output[:] = something`)"""
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

    @staticmethod
    def evaluate(variable_values, parameters, output):
        # We're reusing arrays kind of aggresively ;-)
        ax = numpy.take(variable_values, parameters["ax"])
        bx = numpy.take(variable_values, parameters["bx"])
        dx = numpy.subtract(bx, ax)

        ay = numpy.take(variable_values, parameters["ay"], out=ax)
        by = numpy.take(variable_values, parameters["by"], out=bx)
        dy = numpy.subtract(by, ay, out=ay)

        angle = numpy.arctan2(dy, dx, out=dx)
        error1 = numpy.subtract(angle, parameters["angle"], out=angle)

        # Normalize the angular differnce using
        # (a + 180°) % 360° - 180°
        # https://stackoverflow.com/questions/1878907/the-smallest-difference-between-2-angles
        tmp = numpy.add(error1, math.pi, out=error1)
        tmp = numpy.remainder(tmp, 2 * math.pi, out=tmp)
        tmp = numpy.subtract(tmp, math.pi, out=tmp)

        # Return error in degrees squared
        numpy.square(tmp, out=output)

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
    @staticmethod
    def evaluate(variable_values, parameters, output):
        # We're reusing arrays kind of aggresively ;-)
        ax1 = numpy.take(variable_values, parameters["ax1"])
        bx1 = numpy.take(variable_values, parameters["bx1"])
        dx1 = numpy.subtract(bx1, ax1)
        ay1 = numpy.take(variable_values, parameters["ay1"], out=ax1)
        by1 = numpy.take(variable_values, parameters["by1"], out=bx1)
        dy1 = numpy.subtract(by1, ay1)

        ax2 = numpy.take(variable_values, parameters["ax2"], out=ax1)
        bx2 = numpy.take(variable_values, parameters["bx2"], out=bx1)
        dx2 = numpy.subtract(bx2, ax2)
        ay2 = numpy.take(variable_values, parameters["ay2"], out=ax1)
        by2 = numpy.take(variable_values, parameters["by2"], out=bx1)
        dy2 = numpy.subtract(by2, ay2, out=ax1)
        raise NotImplementedError()

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
