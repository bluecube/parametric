import collections_extended
import numpy

import collections
import itertools

from . import util


class Solver:
    def __init__(self):
        self._constraints = {}  # Indexed by responsible class, contains _ConstraintBlock instance
        self._variable_indices = {}  # Indexed by variable, contains index in self._variables array
        self._variables = []

        self.auto_solve = True

    def add_constraint(self, constraint):
        """ Add a strong constraint to the system to be solved.
        Also adds all variables referenced from the constraint """

        # First number and link in variables
        for o in constraint.get_objects():
            for v in o.get_variables():
                assert (
                    v not in self._variables
                    or constraint not in self._variables[v].constraints
                )
                self._variables.setdefault(v, set())
                self._variables[v].constraints.add(constraint)

        # Then link in the
        responsible_class = self._get_responsible_class(constraint)
        if responsible_class not in self._constraints:
            self._constraints[responsible_class] = _ConstraintBlock()

        self.constraints.append(constraint)
        self.parameter_array.append(constraint.get_parameters(self.solver))

        assert len(self.contains) == len(self.parameter_array)

        assert self._check_state()
        self._auto_solve()

    def remove_constraint(self, constraint):
        responsible_class = self._get_responsible_class(constraint)

        for o in constraint.get_objects():
            for v in o.get_variables():
                self._variables.add(v)

        self._constraints[responsible_class].remove_constraint(constraint)
        if len(self._constraints[responsible_class].constraints) == 0:
            del self._constraints[responsible_class]

        assert self._check_state()
        self._auto_solve()

    def solve(self):
        variables = dict(zip(self._variables, itertools.count()))
        print(variables)
        return
        raise NotImplementedError()

    def _check_state(self):
        """ Asserts that the inner state of the solver is ok and everything is
        linked where it should. """

        constraints_from_variables = set()
        variable_indices = numpy.zeros((len(self._variables),), dtype=bool)
        for var, (index, var_constraints) in self._variables.items():
            try:
                variable_indices[index] = True
            except IndexError:
                if index >= len(self._variables):
                    raise AssertionError("Variable numbering is not continuous")
                elif index < 0:
                    raise AssertionError("Negative variable number?")
                else:
                    raise

            constraints_from_variables.update(var_constraints)

        assert all(variable_indices), "Variable numbering contains duplicates"

        for responsible_class, block in self._constraints.items():
            assert block.responsible_class is responsible_class
            assert block.solver is self
            assert len(block.constraints) == len(block.parameter_array)
            assert len(block.constraints) > 0, "Empty constraint block"
            for i, constraint in block.constraints:
                assert block.parameter_array[i] == constraint.get_parameters(self)
                for o in constraint.get_objects():
                    for v in o.get_variables():
                        assert (
                            v in self._variables
                        ), "Variable referenced from an added constraint is not in variables list"
                        assert (
                            constraint in self._variables[v][1]
                        ), "Constraint is not linked to its variable"

        for constraint in constraints_from_variables:
            responsible_class = self._get_responsible_class(constraint)
            assert (
                constraint in self._constraints[responsible_class].constraints
            ), "Constraint referenced from variable but not stored in the correct constraint block"

        return (
            True
        )  # Returns True only to allow using this method as `assert self._check_state()`

    def _auto_solve(self):
        if self.auto_solve:
            self.solve()

    @staticmethod
    def _get_responsible_class(constraint):
        """ Return a class that handles evaluations for given constraint. """
        # TODO: Properly support subclassing constraints
        ret = constraint.__class__
        assert isinstance(constraint, ret)
        return ret


class _VariableRecord:
    __slots__ = ("index", "constraints")

    def __init__(self, index):
        self.index = index
        self.constraints = set()


class _ConstraintBlock:
    """ Group of constraints of the same type (sharing the same responsible class),
    that can be evaluated togetgher using numpy """

    __slots__ = ("constraints", "parameter_array")

    def __init__(self):
        self.constraints = collections_extended.setlist()
        self.parameter_array = util.DynamicArray(
            dtype=responsible_class.parameters_dtype
        )

    def remove_constraint(constraint):
        """ Remove constraint from a block.
        Reorders the constraints. """
        index = self.constraints.index(constraint)
        self.constraints[index] = self.constraints.pop()
        self.parameter_array[index] = self.parameter_array.pop()

        assert len(self.contains) == len(self.parameter_array)

    def evaluate(self, variable_values):
        return self.responsible_class.evaluate(variable_values, self.parameter_array)
