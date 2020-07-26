import pytest

from bwc.util import immutablize


class ImmutablizeTests:
    def test_basic_1(self):
        immutablize(1)

    def test_basic_2(self):
        with pytest.raises(AttributeError):
            immutablize(1).test = 3
