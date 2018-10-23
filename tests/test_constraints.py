import pytest

from parametric.constraints import *
from parametric.objects import *


def get_constraint_parameters(c):
    dtype = []
    variable_values = []
    parameters = []
    for name, value in c.get_parameters():
        if isinstance(value, Variable):
            dtype.append((name, int))
            parameters.append(len(variable_values))
            variable_values.append(float(value))
        else:
            dtype.append((name, float))
            parameters.append(value)

    return (
        numpy.array(variable_values, dtype=float),
        numpy.array(parameters, dtype=dtype),
    )


@pytest.mark.parametrize(
    "constraint",
    [
        VariableFixed(Variable(5), 3),
        Angle(
            LineSegment(
                Point(Variable(0), Variable(0)), Point(Variable(10), Variable(0))
            ),
            45,
        ),
        Perpendicular(
            LineSegment(
                Point(Variable(0), Variable(0)), Point(Variable(10), Variable(0))
            ),
            LineSegment(
                Point(Variable(1), Variable(1)), Point(Variable(10), Variable(0))
            ),
        ),
    ],
)
def test_constraint_evaluate(constraint):
    values, parameters = get_constraint_parameters(constraint)

    def eval_func(values):
        return constraint.__class__.evaluate(values, parameters)

    print()
    print(type(constraint))
    print(eval_func(values))
    print(autograd.jacobian(eval_func)(values))  # noqa
