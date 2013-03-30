import expressions
import nose.tools

x = expressions.Variable(10)
y = expressions.Variable(2)

def test1():
    expr = x - y

    nose.tools.assert_equals(expr.get_value(), 8)

    pds = expr.get_pds()
    nose.tools.assert_equals(set(pds.keys()), {x, y})
    nose.tools.assert_equals(pds[x], 1)
    nose.tools.assert_equals(pds[y], -1)

