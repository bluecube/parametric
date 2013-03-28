import drawables

def var(value):
    if isinstance(value, Variable):
        return value
    else:
        return Variable(value)

class Variable(object):
    """ Variable used as an parameter of the model.
    Keeps a set of drawables that use it. """

    def __init__(self, value):
        self.value = value
