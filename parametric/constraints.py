import math

import autograd
import autograd.numpy as numpy  # Wrapper to allow differentiating numpy functions

# Work around missing arctan2 vjp in autograd version 1.2
# The impormentation is mostly copied from unreleased autograd commit 47019791
# Autograd, why U no release!?
autograd.extend.defvjp(
    numpy.arctan2,
    lambda ans, x, y: lambda g: g * y / (x ** 2 + y ** 2),
    lambda ans, x, y: lambda g: g * -x / (x ** 2 + y ** 2),
)


class _Constraint:
    @staticmethod
    def evaluate(variable_values, parameters, output):
        """ Calculate error terms for each of the constraints in parameters.
        Error term should either be either in distance units or radians.
        This is not strictly necessary, but will probably speed up the solver a bit.

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

    @staticmethod
    def evaluate(variable_values, parameters):
        return variable_values[parameters["variable"]] - parameters["value"]

    def __init__(self, variable, value):
        self.variable = variable
        self.value = value

    def get_parameters(self):
        return [("variable", self.variable), ("value", self.value)]


class Angle(_Constraint):
    """ Line absolute angle """

    @staticmethod
    def evaluate(variable_values, parameters):
        ax = variable_values[parameters["ax"]]
        bx = variable_values[parameters["bx"]]
        dx = bx - ax
        ay = variable_values[parameters["ay"]]
        by = variable_values[parameters["by"]]
        dy = by - ay

        angle = numpy.arctan2(dy, dx)
        error1 = angle - parameters["angle"]

        # Normalize the angular differnce using
        # (a + 180°) % 360° - 180°
        # https://stackoverflow.com/questions/1878907/the-smallest-difference-between-2-angles
        return numpy.remainder(error1 + math.pi, 2 * math.pi) - math.pi

    def __init__(self, line, angle):
        self.line = line
        self.angle = angle

    def get_parameters(self):
        return [
            ("ax", self.line.a.x),
            ("ay", self.line.a.y),
            ("bx", self.line.b.x),
            ("by", self.line.b.y),
            ("angle", math.radians(self.angle)),
        ]


class Perpendicular(_Constraint):
    @staticmethod
    def evaluate(variable_values, parameters):
        ax1 = variable_values[parameters["ax1"]]
        bx1 = variable_values[parameters["bx1"]]
        dx1 = bx1 - ax1
        ay1 = variable_values[parameters["ay1"]]
        by1 = variable_values[parameters["by1"]]
        dy1 = by1 - ay1
        len1_2 = dx1 * dx1 + dy1 * dy1

        ax2 = variable_values[parameters["ax2"]]
        bx2 = variable_values[parameters["bx2"]]
        dx2 = bx2 - ax2
        ay2 = variable_values[parameters["ay2"]]
        by2 = variable_values[parameters["by2"]]
        dy2 = by2 - ay2
        len2_2 = dx2 * dx2 + dy2 * dy2

        target_length = numpy.sqrt(len1_2 + len2_2)
        actual_length = numpy.hypot(dx1 - dx2, dy1 - dy2)

        return actual_length - target_length

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
    @staticmethod
    def evaluate(variable_values, parameters):
        # TODO: Reuse arrays more
        ax = variable_values[parameters["ax"]]
        bx = variable_values[parameters["bx"]]
        dx = bx - ax
        ay = variable_values[parameters["ay"]]
        by = variable_values[parameters["by"]]
        dy = by - ay
        length = numpy.sqrt(dx * dx + dy * dy)

        return length - parameters["length"]

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
    # TODO: When two variables are equal one of them should be removed from the
    # solver and replaced by the other in all uses
    @staticmethod
    def evaluate(variable_values, parameters):
        return variable_values[parameters["v1"]] - variable_values[parameters["v2"]]

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
