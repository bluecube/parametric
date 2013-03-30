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
    return _Sq(*_wrap_const(a))

def neg(a):
    return _Sub(_Constant(0), _wrap_const(a)[0])

def sqrt(a):
    return _Sqrt(*_wrap_const(a))

def pow(a, b):
    return _Pow(_wrap_const(a)[0], b)

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


class Variable(Expr):
    """ Variable used as an parameter of the model. """

    def __init__(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    def update_value(self, difference):
        self._value += difference

    def get_pds(self):
        return {self: 1}


class _Constant(Expr):
    def __init__(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def get_pds(self):
        return {}


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


class _Sub(Expr):
    def __init__(self, f, g):
        self._f = f
        self._g = g

    def get_value(self):
        return self._f.get_value() - self._g.get_value()

    def get_pds(self):
        ret = self._f.get_pds()
        for var, pd in self._g.get_pds().items():
            pd = ret.get(var, 0) - pd
            ret[var] = pd
        return ret


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

        tmp = 1 / g_val * g_val

        return {
            var: tmp * (f_pds.get(var, 0) * g_val - g_pds.get(var, 0) * f_val)
            for var in all_vars}


#class _Pow(Expr):
#    def __init__(self, f, power):
#        self._f = f
#        self._power = power
#
#    def get_value(self):
#        return self._f.get_value() ** self._power
#
#    def get_pds(self):
#        tmp = (self._power) * self._f.get_value() ** (self.power - 1)
#        return {var: tmp * pd for var, pd in self._f.get_pds()}


class _Sq(Expr):
    def __init__(self, f):
        self._f = f

    def get_value(self):
        val = self._f.get_value()
        return val * val

    def get_pds(self):
        val = self._f.get_value()
        return {var: 2 * val * pd for var, pd in self._f.get_pds().items()}


class _Sqrt(Expr):
    def __init__(self, f):
        self._f = f

    def get_value(self):
        return math.sqrt(self._f.get_value())

    def get_pds(self):
        tmp = 2 / math.sqrt(self._f.get_value())
        return {var: tmp * pd for var, pd in self._f.get_pds().items() if pd != 0}


class _Acos(Expr):
    def __init__(self, f):
        self._f = f

    def get_value(self):
        return math.acos(self._f.get_value())

    def get_pds(self):
        tmp = -1 / math.sqrt(1 - self._f.get_value())
        return {var: tmp * pd for var, pd in self._f.get_pds().items() if pd != 0}



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
