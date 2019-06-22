import pytest


def test():
    assert True is True
    with pytest.raises(ZeroDivisionError):
        assert (1 / 0) == 0
