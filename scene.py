import numpy

class Scene:
    def __init__(self):
        self._primitives = []

        self._constraints = []
        self._variables = set()

    def add_primitive(self, primitive):
        self._primitives.append(primitive)
        for var in primitive.variables:
            self._variables.update(var.expand())

    def add_constraint(self, constraint):
        self._constraints.append(constraint)
        constraint.update()

    def solve(self):
        pds = {}
        variables_map = {}
        variables = list(self._variables)

        for i, var in enumerate(variables):
            variables_map[var] = i

        for i in range(5):
            jacobian = numpy.matrix(numpy.zeros(
                shape=(len(self._constraints), len(self._variables))))
            for constraint_id, constraint in enumerate(self._constraints):
                for var, pd in constraint.get_error_pds().items():
                    var_id = variables_map[var]

                    jacobian[constraint_id, var_id] += pd

            print([constraint.get_error() for constraint in self._constraints])
            errors = numpy.matrix([constraint.get_error() for constraint in self._constraints])

            corrections = numpy.linalg.pinv(jacobian) * errors.T

            for var, correction in zip(variables, corrections.flat):
                var.value -= correction


            with open("/tmp/test{}.svg".format(i), "w") as fp:
                self.export_svg(fp, 100)

    def export_svg(self, fp, scale = 100):
        fp.write('<svg xmlns="http://www.w3.org/2000/svg">\n')
        for primitive in self._primitives:
            primitive.export_svg(fp, scale)
        fp.write('</svg>\n')
