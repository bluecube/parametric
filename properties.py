import expressions as e

def length(a):
    return a.length

def angle(a, b):
    ax = a.p2.x - a.p1.x
    ay = a.p2.y - a.p1.y
    bx = b.p2.x - b.p1.x
    by = b.p2.y - b.p1.y

    dot = e.dot_product(ax, ay, bx, by)
    len_a_squared = e.dot_product(ax, ay, ax, ay)
    len_b_squared = e.dot_product(bx, by, bx, by)

    return e.acos(dot / e.sqrt(len_a_squared * len_b_squared))
