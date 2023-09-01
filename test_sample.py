from sample import (add, min, Cry)

def test_add():
    result=add(1,2)
    expected = 3
    assert result==expected

def test_min():
    result=min(5,3)
    expected = 3
    assert result==expected

def test_cry():
    result=Cry()
    expected = None
    assert result==expected