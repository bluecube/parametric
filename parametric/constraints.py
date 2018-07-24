class _Constraint:
    def get_variables(self):
        for o in self.get_objects():
            yield from o.get_variables()


class VariableFixed(_Constraint):
    def __init__(self, variable):
        self.variable = variable

    def get_objects(self):
        yield self.variable


class PointFixed(_Constraint):
    def __init__(self, point):
        self.point = point

    def get_objects(self):
        yield self.point


class Angle(_Constraint):
    def __init__(self, line, angle):
        self.line = line
        self.angle = angle

    def get_objects(self):
        yield self.line


class Perpendicular(_Constraint):
    def __init__(self, line1, line2):
        self.line1 = line1
        self.line2 = line2

    def get_objects(self):
        yield self.line1
        yield self.line2


class Length(_Constraint):
    def __init__(self, line, length):
        self.line = line
        self.length = length

    def get_objects(self):
        yield self.line


class VariablesEqual(_Constraint):
    def __init__(self, variable1, variable2):
        self.variable1 = variable1
        self.variable2 = variable2

    def get_objects(self):
        yield self.variable1
        yield self.variable2

    def get_variables(self):
        yield self.variable1
        yield self.variable2


class Vertical(VariablesEqual):
    def __init__(self, point1, point2):
        super().__init__(point1.x, point2.x)
        self.point1 = point1
        self.point2 = point2

    def get_objects(self):
        yield self.point1
        yield self.point2


class Horizontal(VariablesEqual):
    def __init__(self, point1, point2):
        super().__init__(point1.y, point2.y)
        self.point1 = point1
        self.point2 = point2

    def get_objects(self):
        yield self.point1
        yield self.point2
