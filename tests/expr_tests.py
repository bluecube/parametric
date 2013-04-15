import expressions as e
import nose.tools

def test1():
    x = e.Variable(10)
    y = e.Variable(2)

    expr = x - y

    nose.tools.assert_equals(expr.get_value(), 8)

    pds = expr.diff_values()
    print(pds)
    nose.tools.assert_equals(set(pds.keys()), {x, y})
    nose.tools.assert_equals(pds[x], 1)
    nose.tools.assert_equals(pds[y], -1)


def check_pds(expr, variables):
    epsilon = 0.0001
    print()

    for var in variables:
        for var2, val in variables.items():
            print(str(var2) + " = " + str(val))
            var2.set_value(val)


        pd = expr.diff(var)
        pd_value = pd.get_value()

        var.update_value(-epsilon)
        value1 = expr.get_value()
        var.update_value(2 * epsilon)
        value2 = expr.get_value()

        numeric_pd = (value2 - value1) / (2 * epsilon)
        print("(d {}) / (d {}) = ({} - {}) / (2 * {}) = {} (expected {} = {})".format(
            str(expr), str(var),
            value2, value1, epsilon, numeric_pd, pd, pd_value))

        nose.tools.assert_almost_equals(numeric_pd, pd_value, delta=epsilon)

def pds_test():
    x = e.Variable(5, "x")
    y = e.Variable(5, "y")
    z = e.Variable(5, "z")

    check_pds(x, {x: 10, y:4})
    check_pds(e.sq(x) + e.sqrt(y) + z, {x: 0.6, y: 10, z: 3})
    check_pds(x - y, {x: 0.6, y: 10})
    check_pds(x * e.pow(y, 4) * z, {x: 0.6, y: 10, z: 3})
    check_pds(x / y, {x: 0.6, y: 10})
    check_pds(e.sq(e.sq(x)), {x: 0.6})
    check_pds(-x, {x: 0.6})
    check_pds(e.sqrt(x), {x: 0.6})
    check_pds(e.pow(x, 2), {x: 0.6})
    check_pds(e.pow(x, 5), {x: 0.6})
    check_pds(e.acos(x), {x: 0.6})


def check_equal_structure(a, b):
    nose.tools.assert_equals(a.__class__, b.__class__)
    nose.tools.assert_equals(len(a._terms), len(b._terms))

    for x, y in zip(a._terms, b._terms):
        check_equal_structure(x, y)

def simplification_test():
    x = e.Variable(5, "x")
    y = e.Variable(5, "y")
    z = e.Variable(5, "z")
    zero = e._Constant(0)
    one = e._Constant(1)

    check_equal_structure(x * y * z, e.mul(x, y, z))

    check_equal_structure(e._Constant(1) * 2 * 3, e._Constant(6))
    check_equal_structure(0 * x, zero)
    check_equal_structure(x * 0, zero)
    check_equal_structure(x * 1 * y * z, x * y * z)
    check_equal_structure(x * 1 * 2 * 3, x * 6)

    check_equal_structure(0 + x, x)
    check_equal_structure(x + 0, x)
    check_equal_structure(x + 1 + 2 + 3, x + 6)

    check_equal_structure(e.neg(2 * x), -2 * x)
    check_equal_structure(e.neg(e.neg(x)), x)
    check_equal_structure(e.inv(e.inv(x)), x)
