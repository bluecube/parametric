from __future__ import division

import functools
import operator
import math

def diff(expression, variable):
    """ Return partial derivative wrt to given variable as an expression """
    return expression._diff(variable)

def numeric_diffs(expression):
    """ Return a dictionary of variable: partial derivative """
    return {var: expression._diff(var).get_value() for var in expression._variables()}

def variables(expression):
    """ Return a set of variables appearing in this expression """
    return _wrap_const(expression)._variables()

def add(*terms):
    return _Add.make_optimized(*terms)

def sub(a, b):
    return _Sub.make_optimized(a, b)

def mul(*terms):
    return _Mul.make_optimized(*terms)

def div(a, b):
    return _Div.make_optimized(a, b)

def sq(a):
    return pow(a, 2)

def neg(a):
    return _Sub.make_optimized(0, a)

def sqrt(a):
    return pow(a, 1/2)

def pow(a, b):
    if b == 2:
        return _Sq.make_optimized(a)
    if b == 1/2:
        return _Sqrt.make_optimized(a)
    else:
        return _Pow.make_optimized(a, b)

def dot_product(ax, ay, bx, by):
    return add(mul(ax, bx), mul(ay, by))

def acos(a):
    return _Acos.make_optimized(a)

def is_constant(expr):
    return isinstance(expr, _Constant)


class Expr(object):
    """ Abstract expression object. """
    @classmethod
    def make_optimized(cls, *terms):
        """ Create a new instance or some optimized equivalent expression.
        Handles constant folding. """
        terms, count = cls._wrap_const(terms)
        instance = cls(*terms)

        if count == 0:
            # There are only constants -- wrap this
            return _Constant(instance.get_value())
        else:
            return instance

    def __init__(self, *terms):
        self._terms = terms

    def get_value(self):
        raise NotImplementedError()

    def _variables(self):
        ret = set()
        for term in self._terms:
            ret.update(term._variables())
        return ret

    def _diff(self, variable):
        """ Return partial derivative of the expression wrt the variable as an expression """
        raise NotImplementedError()

    def __add__(self, other):
        return add(self, other)

    def __radd__(self, other):
        return add(other, self)

    def __sub__(self, other):
        return sub(self, other)

    def __rsub__(self, other):
        return sub(other, self)

    def __mul__(self, other):
        return mul(self, other)

    def __rmul__(self, other):
        return mul(other, self)

    def __truediv__(self, other):
        return div(self, other)

    def __rtruediv__(self, other):
        return div(other, self)

    def __neg__(self):
        return neg(self)

    def __float__(self):
        return float(self.get_value())

    def __str__(self):
        raise NotImplementedError()

    def _str_infix_helper(self, op, alternative_terms = None):
        if alternative_terms is None:
            terms = self._terms
        else:
            terms = alternative_terms
        return "(" + (" " + op + " ").join(str(term) for term in terms) + ")"

    def _str_func_helper(self, func, alternative_terms = None):
        if alternative_terms is None:
            terms = self._terms
        else:
            terms = alternative_terms
        return func + "(" + ", ".join( str(term) for term in terms) + ")"

    @staticmethod
    def _wrap_const(terms):
        """ Return a list of terms with constants wrapped in _Constant and a count
        of non-const expressions. """
        new_terms = []
        non_const_count = 0
        for term in terms:
            if not isinstance(term, Expr):
                new_terms.append(_Constant(term))
            elif isinstance(term, _Constant):
                new_terms.append(term)
            else:
                non_const_count += 1
                new_terms.append(term)

        return new_terms, non_const_count

class _Comutative(Expr):
    """ Base class for comutative operations. As an optimalization, we
    treat comutative operations as n-ary instead of binary only. """

    @classmethod
    def make_optimized(cls, *terms):
        const_instance, terms = cls._process_terms(terms)

        if len(terms) == 0:
            return const_instance

        if cls.absorbing_element is not None and const_instance.get_value() == cls.absorbing_element:
            return _Constant(cls.absorbing_element)
        if const_instance.get_value() != cls.neutral_element:
            terms.append(const_instance)

        if len(terms) == 1:
            return terms[0]

        return cls(*terms)

    def __init__(self, *terms):
        super().__init__(*terms)

    def get_value(self):
        return math.fsum(x.get_value() for x in self._terms)

    def _diff(self, var):
        return add(*[x._diff(var) for x in self._terms])

    def __str__(self):
        return self._str_infix_helper("+")

    @classmethod
    def _process_terms(cls, terms):
        """ Helper method for optimizing commutative operations.
        Return a const part of the terms (all const terms operationed together)
        and a list of non-constants.
        Non-Expression subclasses are converted to _Constant.
        Terms of cls subclasses are processed instead, as if they
        appeared in terms themselves (add(a, add(b, c)) == add(a, b, c)). """
        const = []
        non_const = []

        def term_expander(src):
            for term in src:
                if isinstance(term, cls):
                    for expanded in term_expander(term._terms):
                        yield expanded
                else:
                    yield term

        for term in term_expander(terms):
            if not isinstance(term, Expr):
                const.append(_Constant(term))
            elif isinstance(term, _Constant):
                const.append(term)
            else:
                non_const.append(term)

        const_instance = _Constant(cls(*const).get_value())

        return const_instance, non_const


class Variable(Expr):
    """ Variable used as an parameter of the model. """

    _auto_naming_counter = 1

    def __init__(self, value, name=None):
        self._value = value

        if name:
            self._name = name
        else:
            self._name = "var" + str(self._auto_naming_counter)
            self.__class__._auto_naming_counter += 1

        super().__init__()

    def _variables(self):
        return {self}

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    def update_value(self, difference):
        self._value += difference

    def _diff(self, var):
        if var == self:
            return _Constant(1)
        else:
            return _Constant(0)

    def __str__(self):
        return self._name


class _Constant(Expr):
    def __init__(self, value):
        self._value = value
        super().__init__()

    def get_value(self):
        return self._value

    def _diff(self, var):
        return _Constant(0)

    def __str__(self):
        return str(self.get_value())


class _Add(_Comutative):
    neutral_element = 0
    absorbing_element = None

    def get_value(self):
        return math.fsum(x.get_value() for x in self._terms)

    def _diff(self, var):
        return add(*[x._diff(var) for x in self._terms])

    def __str__(self):
        return self._str_infix_helper("+")


class _Sub(Expr):
    def __init__(self, f, g):
        self._f = f
        self._g = g
        super().__init__(f, g)

    def get_value(self):
        return self._f.get_value() - self._g.get_value()

    def _diff(self, var):
        return self._f._diff(var) - self._g._diff(var)

    def __str__(self):
        return self._str_infix_helper("-")


class _Mul(_Comutative):
    neutral_element = 1
    absorbing_element = 0

    def get_value(self):
        return functools.reduce(operator.mul, [term.get_value() for term in self._terms], 1)

    def _diff(self, var):
        values = [term.get_value() for term in self._terms]

        tmp = []

        for i, term in enumerate(self._terms):
            tmp.append(mul(term._diff(var),
                       *[self._terms[j] for j in range(len(self._terms)) if i != j]))

        return add(*tmp)

    def __str__(self):
        return self._str_infix_helper("*")


class _Div(Expr):
    def __init__(self, f, g):
        self._f = f
        self._g = g
        super().__init__(f, g)

    def get_value(self):
        return self._f.get_value() / self._g.get_value()

    def _diff(self, var):
        g_squared = self._g * self._g
        return (self._f._diff(var) * self._g -
                self._f * self._g._diff(var)) / ( self._g * self._g)

    def __str__(self):
        return self._str_infix_helper("/")


class _Pow(Expr):
    def __init__(self, f, power):
        self._f = f
        self._power = power
        if not is_constant(power):
            raise ValueError("Power has to be constant for now")
        super().__init__(f, power)

    def get_value(self):
        return self._f.get_value() ** self._power.get_value()

    def _diff(self, var):
        return self._power * pow(self._f, self._power - 1) * self._f._diff(var)

    def __str__(self):
        return self._str_infix_helper("**")

class _Sq(_Pow):
    def __init__(self, f):
        super().__init__(f, _Constant(2))

    def get_value(self):
        val = self._f.get_value()
        return val * val

    def _diff(self, var):
        return _Constant(2) * self._f * self._f._diff(var)

    def __str__(self):
        return self._str_func_helper("sq", [self._f])


class _Sqrt(_Pow):
    def __init__(self, f):
        self._f = f
        super().__init__(f, _Constant(1/2))

    def get_value(self):
        return math.sqrt(self._f.get_value())

    def _diff(self, var):
        return _Constant(1/2) * self._f._diff(var) / sqrt(self._f)

    def __str__(self):
        return self._str_func_helper("sqrt", [self._f])


class _Acos(Expr):
    def __init__(self, f):
        self._f = f
        super().__init__(f)

    def get_value(self):
        return math.acos(self._f.get_value())

    def _diff(self, var):
        return -self._f._diff(var) / sqrt(1 - sq(self._f))

    def __str__(self):
        return self._str_func_helper("acos")

