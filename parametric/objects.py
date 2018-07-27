class Variable:
    def __init__(self, value=None, fixed=False):
        self._solver = None
        self._index = None
        self._value = value
        self.fixed = fixed

    def get_variables(self):
        yield self

    def __float__(self):
        return self._value

    def __str__(self):
        ret = str(float(self))
        if not self._solver:
            ret += "(not assigned)"
        return ret


class Point:
    def __init__(self, x=None, y=None, fixed=False):
        self.fixed = fixed
        self.x = Variable(x, fixed)
        self.y = Variable(y, fixed)

    def get_variables(self):
        yield self.x
        yield self.y

    def get_fixing_constraints(self):
        yield


class LineSegment:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def get_variables(self):
        yield from self.a.get_variables()
        yield from self.b.get_variables()
