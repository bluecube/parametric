import collections_extended
import numpy

import collections
import itertools

from . import util
from . import objects


class Solver:
    _variable_index_dtype = numpy.uint32
    _number_dtype = numpy.float64

    def __init__(self):
        self._variables = util.IndexedDict()  # variable -> bag of constraints
        self._objects = {}  # object -> count
        self._constraints = {}  # responsible class -> _ConstraintBlock

        self.auto_solve = True

    def add_constraint(self, constraint):
        responsible_class = self._get_responsible_class(constraint)
        try:
            block = self._constraints[responsible_class]
        except KeyError:
            block = None
        else:
            if constraint in block.constraints:
                raise ValueError("Constraint already registered")

        constraint_parameters = constraint.get_parameters()
        for var in self._constraint_variables(constraint_parameters):
            variable_constraints = self._variables.setdefault(var, collections_extended.bag())
            variable_constraints.add(constraint)

        dtype, parameter_values = self._constraint_parameters(constraint_parameters)
        if block is None:
            block = _ConstraintBlock(dtype)
            self._constraints[responsible_class] = block

        assert block.parameter_array.dtype == dtype
        block.constraints.append(constraint)
        block.parameter_array.append(parameter_values)

        assert self._assert_internal_state()
        self._auto_solve()

    def remove_constraint(self, constraint):
        responsible_class = self._get_responsible_class(constraint)
        try:
            block = self._constraints[responsible_class]
        except KeyError:
            block = None
        if block is None or constraint not in block.constraints:
            raise ValueError("Constraint not registered")

        constraints_to_fix = set()

        for var in self._constraint_variables(constraint.get_parameters()):
            variable_constraints = self._variables[var]
            variable_constraints.remove(constraint)
            if len(variable_constraints) == 0:
                _, new_index, moved_var, moved_var_constraints = self._variables.fast_pop(var)
                constraints_to_fix.update(moved_var_constraints)
        assert constraint not in constraints_to_fix

        if len(block.constraints) == 0:
            # last constraint of this responsible class
            del self._constraints[responsible_class]
        else:
           block.fast_pop(constraint)

        for c in constraints_to_fix:
            responsible_class = self._get_responsible_class(constraint)
            block = self._constraints[responsible_class]

            dtype, parameter_values = self._constraint_parameters(c.get_parameters())
            assert block.parameter_array.dtype == dtype
            index = block.constraints.index(c)
            block.parameter_array[index] = parameter_values

        assert self._assert_internal_state()
        self._auto_solve()

    def solve(self):
        initial = numpy.fromiter(
            (float(var) for var in self._variables),
            dtype=self._number_dtype,
            count=len(self._variables)
        )
        return

    def _print_internal_state(self):
        for index, (var, constraints) in enumerate(self._variables.items()):
            print("variables[{}]: {}, used by {}".format(index, var, constraints))
        for responsible_class, block in self._constraints.items():
            print(responsible_class)
            for constraint in block.constraints:
                print("  ", str(constraint))

    def _assert_internal_state(self):
        """ Asserts that the inner state of the solver is ok and everything is
        linked where it should. """

        self._variables._assert_internal_state()  # I still don't 100% trust IndexedDict :)

        constraints_from_variables = collections_extended.bag()
        for var_constraints in self._variables.values():
            constraints_from_variables |= var_constraints

        for constraint in constraints_from_variables:
            responsible_class = self._get_responsible_class(constraint)
            assert constraint in self._constraints[responsible_class].constraints

        for responsible_class, block in self._constraints.items():
            assert len(block.constraints) == len(block.parameter_array)
            assert len(block.constraints) > 0, "Empty constraint block"
            for i, constraint in enumerate(block.constraints):
                assert constraint in constraints_from_variables

                constraint_parameters = constraint.get_parameters()
                constraint_variables = self._constraint_variables(constraint_parameters)
                assert len(constraint_variables) > 0
                for v in constraint_variables:
                    assert v in self._variables
                    assert constraint in self._variables[v]

                dtype, values = self._constraint_parameters(constraint_parameters)
                assert block.parameter_array.dtype == dtype
                assert tuple(block.parameter_array[i]) == values

        # Returns True to allow using this method as `assert self._assert_internal_state()`
        return True

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

    def _constraint_variables(self, parameters):
        return [v for _, v in parameters if isinstance(v, objects.Variable)]

    def _constraint_parameters(self, parameters):
        dtype = []
        values = []
        for name, value in parameters:
            if isinstance(value, objects.Variable):
                dtype.append((name, self._variable_index_dtype))
                values.append(self._variables.index(value))
            else:
                dtype.append((name, self._number_dtype))
                values.append(value)

        return dtype, tuple(values)


class _VariableRecord:
    __slots__ = ("index", "constraints")

    def __init__(self, index):
        self.index = index
        self.constraints = set()


class _ConstraintBlock:
    """ Group of constraints of the same type (sharing the same responsible class),
    that can be evaluated togetgher using numpy """

    __slots__ = ("constraints", "parameter_array")

    def __init__(self, dtype):
        self.constraints = collections_extended.setlist()
        self.parameter_array = util.DynamicArray(dtype=dtype)

    def fast_pop(self, constraint):
        """ Swap the deleted constraint to the back and pop """
        index = self.constraints.index(constraint)
        if index != len(self.constraints) - 1:
            self.constraints[index] = self.constraints[-1]
            self.parameter_array[index] = self.parameter_array[-1]
        self.constraints.pop()
        self.parameter_array.pop()
