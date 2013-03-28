class Drawable(object):
    def export_svg(self, fp, scale):
        """ Write SVG code for this drawable to file. """
        raise NotImplementedError()

