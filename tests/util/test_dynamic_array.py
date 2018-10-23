# pylint: disable=redefined-outer-name
# pylint: disable=W0212

import numpy
import pytest

from parametric.util import DynamicArray


@pytest.mark.parametrize(
    "dtype", [None, numpy.int8, bytes, [("big", ">i4"), ("little", "<i4")], int]
)
@pytest.mark.parametrize("size_hint", [None, 0, 1, 10, 100])
def test_construction_empty(dtype, size_hint):
    da = DynamicArray(dtype=dtype, size_hint=size_hint)

    assert len(da) == 0
    with pytest.raises(IndexError):
        da[1]  # noqa
    if size_hint:
        assert len(da._array) == size_hint


def test_append():
    da = DynamicArray(dtype=int, size_hint=10)

    for i in range(100):
        da.append(97 * i % 100)

    assert len(da) == 100
    assert len(da._array) >= 100


class Weirdo:
    def __len__(self):
        return 5

    def __iter__(self):
        return iter(range(5))


@pytest.mark.parametrize(
    "value, dtype",
    [
        ([1, 2, 3], int),
        (range(5), int),
        (numpy.arange(8), float),
        (numpy.arange(8), complex),
        (Weirdo(), int),
    ],
)
@pytest.mark.parametrize("size_hint", [None, 0, 1, 100])
def test_extend(value, dtype, size_hint):
    da = DynamicArray(dtype=dtype, size_hint=size_hint)

    da.extend(value)
    assert list(da) == list(value)
    da.extend(value)
    assert list(da) == list(value) + list(value)


def test_extend_iterator():
    da = DynamicArray(dtype=int)
    da.extend(iter(range(5)))
    assert list(da) == list(range(5))


@pytest.fixture
def array():
    da = DynamicArray(dtype=int)
    da.extend(range(100))
    return da


def test_pop(array):
    l = len(array)
    assert array.pop() == l - 1
    assert len(array) == l - 1
    assert list(array) == list(range(l - 1))


def test_pop_all(array):
    while len(array):
        array.pop()

    assert 100 > len(array._array) > 0

    with pytest.raises(IndexError):
        array.pop()


def test_pop_n(array):
    n = 50
    l = len(array)
    array.pop_n(n)

    assert len(array) == l - n
    assert list(array) == list(range(l - n))
    assert 100 > len(array._array) > 0


def test_indexing_single(array):
    for i in range(len(array)):  # noqa
        assert array[i] == i


def test_indexing_slices(array):
    for i in range(5):
        offset = i * 20
        for j in range(5):
            count = 3 * j + 1

            assert list(array[offset : offset + count]) == list(
                range(offset, offset + count)
            )


@pytest.mark.parametrize("dtype", [int, float, complex])
def test_array_protocol(array, dtype):
    numpy.array(array, dtype=dtype)


def test_record_dtype():
    array = DynamicArray(dtype=[("a", numpy.int32), ("b", numpy.float32)])
    for i in range(100):
        array.append((i, i + 0.5))

    assert list(array["a"]) == list(range(100))
    assert list(array["b"] - 0.5) == list(range(100))
