from __future__ import division

import functools
import operator
import math

def diff(expression, variable):
    """ Return partial derivative wrt to given variable as an expression """
    return _wrap_const(expression)._diff(variable)

def numeric_diffs(expression):
    """ Return a dictionary of variable: partial derivative """
    expression = _wrap_const(expression)
    return {var: expression._diff(var).get_value() for var in expression._variables()}

def variables(expression):
    """ Return a set of variables appearing in this expression """
    return _wrap_const(expression)._variables()

def add(*terms):
    return _Add(*_wrap_consts(*terms))

def sub(a, b):
    return _Sub(*_wrap_consts(a, b))

def mul(*terms):
    return _Mul(*_wrap_consts(*terms))

def div(a, b):
    return _Div(*_wrap_consts(a, b))

def sq(a):
    return pow(a, 2)

def neg(a):
    return _Sub(_Constant(0), _wrap_const(a))

def sqrt(a):
    return pow(a, 1/2)

def pow(a, b):
    a = _wrap_const(a)
    if b == 2:
        return _Sq(a)
    if b == 1/2:
        return _Sqrt(a)
    else:
        return _Pow(a, b)

def dot_product(ax, ay, bx, by):
    ax, ay, bx, by = _wrap_const(ax, ay, bx, by)
    return ax * bx + ay * by

def acos(a):
    return _Acos(_wrap_const(a))


class Expr(object):
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

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self._terms == other._terms

    def __str__(self):
        raise NotImplementedError()

    def _str_infix_helper(self, op):
        return "(" + (" " + op + " ").join(str(term) for term in self._terms) + ")"

    def _str_func_helper(self, func):
        return func + "(" + ", ".join( str(term) for term in self._terms) + ")"


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

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return id(self) == id(other)

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

class _Add(Expr):
    def __init__(self, *terms):
        super().__init__(*terms)

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


class _Mul(Expr):
    def __init__(self, *terms):
        super().__init__(*terms)

    def get_value(self):
        return functools.reduce(operator.mul, [term.get_value() for term in self._terms])

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
        super().__init__(f)

    def get_value(self):
        return self._f.get_value() ** self._power

    def _diff(self, var):
        return _Constant(self._power) * pow(self._f, self._power - 1) * self._f._diff(var)

    def __str__(self):
        return "(" + str(self._f) + "^" + str(self._power) + ")"

class _Sq(_Pow):
    def __init__(self, f):
        super().__init__(f, 2)

    def get_value(self):
        val = self._f.get_value()
        return val * val

    def _diff(self, var):
        return _Constant(2) * self._f * self._f._diff(var)

    def __str__(self):
        return self._str_func_helper("sq")


class _Sqrt(_Pow):
    def __init__(self, f):
        self._f = f
        super().__init__(f, 1/2)

    def get_value(self):
        return math.sqrt(self._f.get_value())

    def _diff(self, var):
        return _Constant(1/2) * self._f._diff(var) / sqrt(self._f)

    def __str__(self):
        return self._str_func_helper("sqrt")


class _Acos(Expr):
    def __init__(self, f):
        self._f = f
        super(_Acos, self).__init__(f)

    def get_value(self):
        return math.acos(self._f.get_value())

    def _diff(self, var):
        return -self._f._diff(var) / sqrt(1 - sq(self._f))

    def __str__(self):
        return self._str_func_helper("acos")


def _wrap_consts(*args):
    return [_wrap_const(x) for x in args]

def _wrap_const(expr):
    return expr if isinstance(expr, Expr) else _Constant(expr)

