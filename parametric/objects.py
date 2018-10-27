import itertools


class Variable:
    def __init__(self, value, name=None):
        self._value = value
        self.name = name

    def get_variables(self):
        yield self

    def __float__(self):
        return float(self._value)

    def __repr__(self):
        return "{}({}, name={})".format(self.__class__.__name__, self._value, self.name)


class Point:
    def __init__(self, x, y, name=None):
        self.x = Variable(x, None if name is None else name + ".x")
        self.y = Variable(y, None if name is None else name + ".y")
        self.name = name

    def get_variables(self):
        yield self.x
        yield self.y

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, repr(self.x), repr(self.y))


class LineSegment:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def get_variables(self):
        yield from self.a.get_variables()
        yield from self.b.get_variables()


class Polyline:
    """ A closed polyline. """

    def __init__(self, coords, name=None):
        """ Make the polyline from a list of pairs with point coordinates """
        self.points = [
            Point(c[0], c[1], None if name is None else "{}[{}]".format(name, i))
            for i, c in enumerate(coords)
        ]
        self.line_segments = [
            LineSegment(p1, p2) for p1, p2 in zip(self.points[:-1], self.points[1:])
        ]
        self.line_segments.append(LineSegment(self.points[-1], self.points[0]))

    def get_variables(self):
        return itertools.chain.from_iterable(p.get_variables() for p in self.points)

    def __getitem__(self, index):
        return self.points[index]

    def __iter__(self):
        return iter(self.points)

    def __len__(self):
        return len(self.points)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.points))
