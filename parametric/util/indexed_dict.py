import collections


class IndexedDict(collections.MutableMapping):
    _marker = object()

    def __init__(self, *args, **kwargs):
        """ Create empty IndexedDict and call self.update(*args, **kwargs). """
        self.clear()
        self.update(*args, **kwargs)

    def clear(self):
        """ Remove all items. """
        self._dict = {}  # key -> (index, value)
        self._list = []  # index -> (key, value)

    def get(self, key=_marker, index=_marker, d=None):
        """ Return value with given key or index.
        If no value is found, return d (None by default). """
        if index is self._marker and key is not self._marker:
            try:
                index, value = self._dict[key]
            except KeyError:
                return d
            else:
                return value
        elif index is not self._marker and key is self._marker:
            try:
                key, value = self._list[index]
            except IndexError:
                return d
            else:
                return value
        else:
            raise self._key_eq_index_error()

    def pop(self, key=_marker, index=_marker, d=_marker):
        """ Remove and return value with given key or index (last item by default).
        If key is not found, d is returned if given, otherwise KeyError or IndexError is raised.
        This is generally O(N) unless removing last item, then O(1). """
        if index is self._marker and key is not self._marker:
            try:
                index, value = self._dict.pop(key)
            except KeyError:
                if d is self._marker:
                    raise
                else:
                    return d
            key2, value2 = self._list.pop(index)
            assert key == key2
        elif key is self._marker:
            try:
                if index is self._marker:
                    index = len(self._list) - 1
                    key, value = self._list.pop()
                else:
                    key, value = self._list.pop(index)
                    if index < 0:
                        index += len(self._list) + 1
            except IndexError:
                if d is self._marker:
                    raise
                else:
                    return d
            index2, value2 = self._dict.pop(key)
            assert index == index2
        else:
            raise self._key_and_index_error()

        assert value is value2

        self._fix_indices_after_delete(index)

        return value

    def fast_pop(self, key=_marker, index=_marker):
        """ Remove value  with given key or index (last item by default) fast
        by swapping it to the last place first.
        Changes order of the remaining items (item that used to be last goes to the
        popped location).
        Returns tuple of (poped_value, new_moved_index, moved_key, moved_value).
        If key is not found raises KeyError or IndexError.
        Runs in O(1). """
        if index is self._marker and key is not self._marker:
            index, popped_value = self._dict.pop(key)
        elif key is self._marker:
            if index is self._marker:
                index = len(self._list) - 1
                key, popped_value2 = self._list[-1]
            else:
                key, popped_value2 = self._list[index]
                if index < 0:
                    index += len(self._list)
            index2, popped_value = self._dict.pop(key)
            assert index == index2
        else:
            raise self._key_and_index_error()

        if key == self._list[-1][0]:
            # The item we're removing happens to be the last in the list, no swapping needed
            _, popped_value2 = self._list.pop()
            assert popped_value is popped_value2
            return popped_value, len(self._list), key, popped_value
        else:
            # Swap the last item onto the deleted spot and pop the last item from the list
            self._list[index] = self._list[-1]
            moved_key, moved_value = self._list.pop()
            self._dict[moved_key] = (index, moved_value)
            return popped_value, index, moved_key, moved_value

    def popitem(self, last=True):
        """ Remove and return last (default) or first (last=False) pair (key, value).
        Raises KeyError if the dictionary is empty.
        Runs in O(1) for last item, O(N) for first one. """
        try:
            if last:
                key, value = self._list.pop()
                index = len(self._list)
            else:
                key, value = self._list.pop(0)
                index = 0
        except IndexError:
            raise KeyError("IndexedDict is empty")

        index2, value2 = self._dict.pop(key)
        assert index == index2
        assert value is value2

        if not last:
            self._fix_indices_after_delete()

        return key, value

    def move_to_end(self, key=_marker, index=_marker, last=True):
        """ Move an existing element to the end (or beginning if last==False). O(N). """
        if index is self._marker and key is not self._marker:
            index, value = self._dict[key]
        elif index is not self._marker and key is self._marker:
            key, value = self._list[index]

            # Normalize index
            if index < 0:
                index += len(self._list)
        else:
            raise self._key_eq_index_error()

        if last:
            index_range = range(len(self._list) - 1, index - 1, -1)
            self._dict[key] = (len(self._list) - 1, value)
        else:
            index_range = range(index + 1)
            self._dict[key] = (0, value)

        previous = (key, value)
        for i in index_range:
            self._dict[previous[0]] = i, previous[1]
            previous, self._list[i] = self._list[i], previous

    def copy(self):
        """ A shallow copy """
        ret = IndexedDict()
        ret._dict = self._dict.copy()
        ret._list = self._list.copy()
        return ret

    def index(self, key):
        """ Return index of a record with given key """
        return self._dict[key][0]

    def key(self, index):
        """ Return key of a record at given index """
        return self._list[index][0]

    def __len__(self):
        return len(self._list)

    def __repr__(self):
        return "IndexedDict({})".format(repr(self._list))

    def __getitem__(self, key):
        return self._dict[key][1]

    def __setitem__(self, key, value):
        if key in self._dict:
            index, old_value1 = self._dict[key]
            self._list[index] = key, value
        else:
            index = len(self._list)
            self._list.append((key, value))
        self._dict[key] = index, value

    def __delitem__(self, key):
        index, value = self._dict.pop(key)
        key2, value2 = self._list.pop(index)
        assert key == key2
        assert value is value2

        self._fix_indices_after_delete(index)

    def __contains__(self, key):
        return key in self._dict

    def __iter__(self):
        return (item[0] for item in self._list)

    @staticmethod
    def _key_and_index_error():
        return TypeError("Specifying both `key` and `index` is not allowed")

    @staticmethod
    def _key_eq_index_error():
        raise TypeError("Exactly one of `key` and `index` must be specified")

    def _fix_indices_after_delete(self, starting_index=0):
        for i, (k, v) in enumerate(self._list[starting_index:], starting_index):
            self._dict[k] = (i, v)

    def _assert_internal_state(self):
        """ Asserts that the inner state of the solver is consistent.
        Returns True, so it can be used in an assert expression itself. """

        assert len(self._dict) == len(self._list)
        for k, (i, v) in self._dict.items():
            k2, v2 = self._list[i]
            assert k2 == k
            assert v2 is v

        return True
