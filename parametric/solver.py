import collections_extended

import collections
import itertools

class OrderedCounter(collections.Counter, collections.OrderedDict):
    pass

class Solver:
    def __init__(self):
        self._constraints = {}  # Indexed by responsible class, contains _ConstraintBlock instance
        self._variables = OrderedCounter()

        self.auto_solve = True

    def add_constraint(self, constraint):
        """ Add a strong constraint to the system to be solved.
        Also adds all objects and variables referenced from the constraint """

        responsible_class = self._get_responsible_class(constraint)


        self._constraints.add(constraint)
        self._objects.update(constraint.get_objects())
        self._variables.update(constraint.get_variables())
        self._auto_solve()

    def remove_constraint(self, constraint):
        self._constraints.remove(constraint)
        self._objects.remove(constraint.get_objects())
        self._variables.remove(constraint.get_variables())
        self._auto_solve()

    def solve(self):
        variables = dict(zip(self._variables, itertools.count()))
        print(variables)
        return
        raise NotImplementedError()

    def _auto_solve(self):
        if self.auto_solve:
            self.solve()

    @staticmethod
    def _get_responsible_class(constraint):
        """ Return a class that handles evaluations for given constraint. """
        #TODO: Properly support subclassing constraints
        return constraint.__class__


class _ConstraintBlock:
    def __init__(self):
        self.constraints = collections_extended.setlist()
        self.index_arrays = None
