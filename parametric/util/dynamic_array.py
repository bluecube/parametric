import numpy


class DynamicArray:
    """ Dynamic 1D array that supports efficient appends (like array.array) based on numpy (supporting dtypes) """

    _initial_size = 10

    def __init__(self, dtype=None, size_hint=None):
        dt = numpy.dtype(dtype)
        if dt.shape != ():
            raise ValueError("Sub-aray dtypes are not supported now")

        initial_size = self._initial_size if size_hint is None else size_hint
        self._array = numpy.zeros((initial_size,), dtype=dtype)
        self.size = 0

    def _update_size(self, size, min_size=0):
        self._array.resize(max(3 * size // 2, min_size))

    def _maybe_inflate(self, size):
        if size > len(self._array):
            self._update_size(size)

    def _maybe_deflate(self, size):
        if size < len(self._array) / 2:
            self._update_size(size, self._initial_size)

    def append(self, value):
        new_size = self.size + 1
        self._maybe_inflate(new_size)
        self._array[self.size] = value
        self.size = new_size

    def pop(self):
        if self.size == 0:
            raise IndexError("Pop from empty array")

        v = self._array[self.size - 1]

        self.size -= 1
        self._maybe_deflate(self.size)

        return v

    def extend(self, values):
        offset = self.size

        try:
            length = len(values)
        except TypeError:
            pass
        else:
            new_size = self.size + length
            self._maybe_inflate(new_size)
            self.size = new_size

            try:
                # First try to do numpy slice assignment for speeed
                self._array[offset : self.size] = values
            except TypeError:
                pass
            else:
                return

            # TODO: Handle objects that report different length than it actualy is
            # (list does that). At that point length and size_hint are basically equivalent
            for i, value in enumerate(values, offset):
                self._array[i] = value
            return

        # TODO: Use size_hint
        for value in values:
            self.append(value)

    def pop_n(self, n):
        if n > self.size:
            raise IndexError("Not enough values to pop")
        self.size -= n
        self._maybe_deflate(self.size)

    def reserve(self, size):
        """ Resize the internal array to size if possible.
        Useful to pre allocate area for later insertions in advance.
        Note that this is one shot only, any following operation will cause the
        the array to resize as normal. """
        self._array.resize(max(self.size, size))

    def shrink(self):
        """ Shrink the internal array as much as possible.
        Equivalent to reserve(0) """
        self._array.resize(self.size)

    def array(self):
        """ Return a slice of the internal numpy array """
        return self._array[: self.size]

    def __array__(self, dtype=None):
        """ To match numpy's protocol """
        if dtype is None:
            return self.array()
        else:
            return self.array(self.array(), dtype=dtype)

    def __getitem__(self, key):
        return self.array()[key]

    def __setitem__(self, key, value):
        self.array()[key] = value

    def __len__(self):
        return self.size

    def __iter__(self):
        return iter(self.array())

    def __str__(self):
        return str(self.array())

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, str(self.array()))
