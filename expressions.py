from __future__ import division

import functools
import operator
import math

def add(*terms):
    return _Add(*_wrap_const(*terms))

def sub(a, b):
    return _Sub(*_wrap_const(a, b))

def mul(*terms):
    return _Mul(*_wrap_const(*terms))

def div(a, b):
    return _Div(*_wrap_const(a, b))

def sq(a):
    return pow(a, 2)

def neg(a):
    return _Sub(_Constant(0), _wrap_const(a)[0])

def sqrt(a):
    return pow(a, 1/2)

def pow(a, b):
    a = _wrap_const(a)[0]
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
    return _Acos(_wrap_const(a)[0])

def _wrap_const(*args):
    return [x if isinstance(x, Expr) else _Constant(x) for x in args]

def _multiply(iterable):
    return functools.reduce(operator.mul, iterable)


class Expr(object):
    def __init__(self, *terms):
        self._terms = terms

    def get_value(self):
        raise NotImplementedError()

    def get_pds(self):
        raise NotImplementedError()

    def __add__(self, other):
        return add(self, other)

    def __sub__(self, other):
        return sub(self, other)

    def __mul__(self, other):
        return mul(self, other)

    def __div__(self, other):
        return div(self, other)

    def __neg__(self):
        return neg(self)

    def __float__(self):
        return float(self.get_value())

    def __str__(self):
        raise NotImplementedError()

    def _term_values(self):
        return (term.get_value() for term in self._terms)

    def _pds_helper(self):
        """ Return list of partial derivatives for each term, and set of variables
        encountered in this list. """
        pds_list = []
        all_vars = set()
        for term in self._terms:
            pds = term.get_pds()
            pds_list.append(pds)
            all_vars.update(pds.keys())
        return pds_list, all_vars

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

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    def update_value(self, difference):
        self._value += difference

    def get_pds(self):
        return {self: 1}

    def __str__(self):
        return self._name


class _Constant(Expr):
    def __init__(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def get_pds(self):
        return {}

    def __str__(self):
        return str(self.get_value())

class _Add(Expr):
    def __init__(self, *terms):
        self._terms = terms

    def get_value(self):
        return math.fsum(x.get_value() for x in self._terms)

    def get_pds(self):
        ret = {}
        for term in self._terms:
            for var, pd in term.get_pds().items():
                pd += ret.get(var, 0)
                ret[var] = pd
        return ret

    def __str__(self):
        return self._str_infix_helper("+")


class _Sub(Expr):
    def __init__(self, f, g):
        self._f = f
        self._g = g
        super(_Sub, self).__init__(f, g)

    def get_value(self):
        return self._f.get_value() - self._g.get_value()

    def get_pds(self):
        ret = self._f.get_pds()
        for var, pd in self._g.get_pds().items():
            pd = ret.get(var, 0) - pd
            ret[var] = pd
        return ret

    def __str__(self):
        return self._str_infix_helper("-")


class _Mul(Expr):
    def __init__(self, *terms):
        super(_Mul, self).__init__(*terms)

    def get_value(self):
        return _multiply(self._term_values())

    def get_pds(self):
        pds_list, all_vars = self._pds_helper()
        term_values = list(self._term_values())
        value = _multiply(term_values)

        return {
            var: math.fsum(value * pds_list[i][var] / term_values[i]
                for i in range(len(self._terms))
                if var in pds_list[i] and term_values[i] != 0)
            for var in all_vars}

    def __str__(self):
        return self._str_infix_helper("*")


class _Div(Expr):
    def __init__(self, f, g):
        self._f = f
        self._g = g
        super(_Div, self).__init__(f, g)

    def get_value(self):
        return self._f.get_value() / self._g.get_value()

    def get_pds(self):
        (f_pds, g_pds), all_vars = self._pds_helper()
        f_val, g_val = self._term_values()

        tmp = 1 / (g_val * g_val)

        return {
            var: tmp * (f_pds.get(var, 0) * g_val - g_pds.get(var, 0) * f_val)
            for var in all_vars}

    def __str__(self):
        return self._str_infix_helper("/")


class _Pow(Expr):
    def __init__(self, f, power):
        self._f = f
        self._power = power

    def get_value(self):
        return self._f.get_value() ** self._power

    def get_pds(self):
        tmp = (self._power) * self._f.get_value() ** (self._power - 1)
        return {var: tmp * pd for var, pd in self._f.get_pds().items()}

    def __str__(self):
        return "(" + str(self._f) + "^" + str(self._power) + ")"

class _Sq(Expr):
    def __init__(self, f):
        self._f = f
        super(_Sq, self).__init__(f)

    def get_value(self):
        val = self._f.get_value()
        return val * val

    def get_pds(self):
        val = self._f.get_value()
        return {var: 2 * val * pd for var, pd in self._f.get_pds().items()}

    def __str__(self):
        return self._str_func_helper("sq")


class _Sqrt(Expr):
    def __init__(self, f):
        self._f = f
        super(_Sqrt, self).__init__(f)

    def get_value(self):
        return math.sqrt(self._f.get_value())

    def get_pds(self):
        tmp = 1 / (2 * math.sqrt(self._f.get_value()))
        return {var: tmp * pd for var, pd in self._f.get_pds().items() if pd != 0}

    def __str__(self):
        return self._str_func_helper("sqrt")


class _Acos(Expr):
    def __init__(self, f):
        self._f = f
        super(_Acos, self).__init__(f)

    def get_value(self):
        return math.acos(self._f.get_value())

    def get_pds(self):
        f_value = self._f.get_value()
        tmp = -1 / math.sqrt(1 - f_value * f_value)
        return {var: tmp * pd for var, pd in self._f.get_pds().items() if pd != 0}

    def __str__(self):
        return self._str_func_helper("acos")


#class DotProduct(Expr):
#    def __init__(self, *terms):
#        """ Takes exactly 8 expressions, ordered like this: [x, y], [p1, p2]. [line1, line2];
#        (line1.p1.x, line1.p1.y, line1.p2.x, ..., line2.p2.y)."""
#        if len(terms) != 8:
#            raise ValueError("Exactly 8 terms objects must be provided")
#
#        self._terms = terms
#
#    def get_value(self):
#        terms = [var.get_value() for var in self._terms]
#        ux = terms[0] - terms[2]
#        uy = terms[1] - terms[3]
#        vx = terms[4] - terms[6]
#        vy = terms[5] - terms[7]
#
#        return ux * vx + uy * vy
#
#    def get_pds(self):
#        val = [var.get_value() for var in self._terms]
#        pds = [var.get_pds() for var in self._terms]
#        terms = set.union(*[x.keys() for x in pds])
#
#        return {
#            (pds[0].get(var, 0) - pds[2].get(var, 0)) * (val[4] - val[6]) +
#            (val[0] - val[2]) * (pds[4].get(var, 0) - pds[6].get(var, 0)) +
#            (pds[1].get(var, 0) - pds[3].get(var, 0)) * (val[5] - val[7]) +
#            (val[1] - val[3]) * (pds[5].get(var, 0) - pds[7].get(var, 0))
#            for var in terms}
#
