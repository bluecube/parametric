import collections_extended
import numpy

import collections
import itertools

from . import util


class Solver:
    _variable_index_dtype = numpy.uint32
    _number_dtype = numpy.float64

    def __init__(self):
        self._variables = util.IndexedDict()  # variable -> set of constraints
        self._objects = {}  # object -> count
        self._constraints = {}  # responsible class -> _ConstraintBlock

        self.auto_solve = True

    def add_constraint(self, constraint):
        dtype, parameter_values, variables = self._constraint_parameters(constraint)

        for var in variables:
            variable_constraints = self._variables.setdefault(v, set())
            assert constraint not in variable_constraints
            variable_constraints.add(constraint)

        responsible_class = self._get_responsible_class(constraint)
        try:
            block = self._constraints[responsible_class]
        except KeyError:
            block = _ConstraintBlock(dtype)
            constraints_dict[responsible_class] = block

        assert block.parameter_array.dtype == dtype
        block.constraints.append(constraint)
        block.parameter_array.append(parameter_values)

        assert self._assert_internal_state()
        self._auto_solve()

    def remove_constraint(self, constraint):
        _, _, variables = self._constraint_parameters(constraint)

        constraints_to_fix = set()

        for var in variables:
            variable_constraints = self._variables[var]
            variable_constraints.remove(constraint)
            if len(variable_constraints) == 0:
                _, new_index, moved_var, moved_var_constraints = self._variables.fast_pop(var)
                constraints_to_fix.update(moved_var_constraints)
        assert constraint not in constraints_to_fix

        responsible_class = self._get_responsible_class(constraint)
        block = self._constraints[responsible_class]
        assert constraint in block.constraints
        if len(block.constraints) == 0:
            # last constraint of this responsible class
            del self._constraints[responsible_class]
        else:
           block.fast_pop(constraint)

        for c in constraints_to_fix:
            responsible_class = self._get_responsible_class(constraint)
            block = self._constraints[responsible_class]

            dtype, parameter_values, _ = self._constraint_parameters(c)
            assert block.parameter_array.dtype == dtype
            index = block.constraints.index(c)
            block.parameter_array[index] = parameter_values

        assert self._assert_internal_state()
        self._auto_solve()

    def solve(self):
        initial = numpy.fromiter(
            (var.value for var in self._variables),
            dtype=self._number_dtype,
            count=len(self._variables)
        )
        print(initial)
        return

    def _assert_internal_state(self):
        """ Asserts that the inner state of the solver is ok and everything is
        linked where it should. """

        self._variables._assert_internal_state()  # I still don't 100% trust IndexedDict :)

        constraints_from_variables = set()
        for var_constraints in self._variables.values():
            constraints_from_variables.update(var_constraints)

        for responsible_class, block in self._constraints.items():
            assert constraint in constraints_from_variables
            assert len(block.constraints) == len(block.parameter_array)
            assert len(block.constraints) > 0, "Empty constraint block"
            for i, constraint in enumerate(block.constraints):
                dtype, values, variables = self._constraint_parameters(constraint)
                assert block.parameter_array.dtype == dtype
                assert block.parameter_array[i] == values
                for v in variables:
                    assert v in self._variables
                    assert constraint in self._variables[v][1]

        for constraint in constraints_from_variables:
            responsible_class = self._get_responsible_class(constraint)
            assert constraint in self._constraints[responsible_class].constraints

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

    def _constraint_parameters(self, constraint):
        dtype = []
        values = []
        variables = []
        for name, value in constraint.get_parameters():
            if isinstance(value, objects.Variable):
                dtype.append((name, self._variable_index_dtype))
                values.append(self._variables.index(x))
                variables.append(value)
            else:
                dtype.append((name, self._number_dtype))
                values.append(x)

        return dtype, tuple(values), variables


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
