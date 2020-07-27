import pytest

from bwc.objects import Player
from bwc.util import immutablize


class TestImmutablize:
    def test_basic_1(self):
        i = immutablize(1)
        assert i.bit_length() == 1

    def test_basic_2(self):
        with pytest.raises(AttributeError):
            immutablize(1).test = 3

    def test_class_1(self):
        class Dummy:
            pass

        immutablize(Dummy())

    def test_class_2(self):
        class Dummy:
            pass

        d = Dummy()
        d.test = 73
        assert immutablize(d).test == 73

    def test_equality_1(self):
        assert immutablize(1) == immutablize(1)

    def test_equality_2(self):
        # Player is an easy object with a custom __eq__ defined
        assert immutablize(Player()) == immutablize(Player())

    def test_arrays_1(self):
        assert immutablize([1, 2, 3])[2] == 3

    def test_arrays_2(self):
        with pytest.raises(AttributeError):
            immutablize([1, 2])[0] = 2

    def test_contains_1(self):
        assert 7 in immutablize([1, 2, 3, 4, 5, 6, 7])
        assert Player() in immutablize([Player(), None, 5])

    def test_function_call(self):
        immutablize({2: 1, 3: 5}).values()

    def test_iteration_basic(self):
        for x in immutablize([1, 2, 3, 4]):
            pass

    def test_non_subclassable(self):
        assert 2 in immutablize(range(10))

    # TODO: make this test work! Currently, the objects returned when iterating over a list are not immutable,
    # because we can't proxy a `list_iterator` object, as
    # def test_iteration_immutable(self):
    #     obj = immutablize([Player(), Player(), Player()])
    #     for x in obj:
    #         with pytest.raises(AttributeError):
    #             x.name = "test"
