
class Variable:
    def __init__(self, value, name=None):
        self._value = value
        self.name = name

    def get_variables(self):
        yield self

    def __float__(self):
        return float(self._value)

    def __str__(self):
        if self.name is None:
            return "Variable at 0x{:x} ({})".format(id(self), float(self))
        else:
            return "Variable {} ({})".format(self.name, float(self))


class Point:
    def __init__(self, x, y, name=None):
        self.x = Variable(x, None if name is None else name + ".x")
        self.y = Variable(y, None if name is None else name + ".y")
        self.name = name

    def get_variables(self):
        yield self.x
        yield self.y


class LineSegment:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def get_variables(self):
        yield from self.a.get_variables()
        yield from self.b.get_variables()

