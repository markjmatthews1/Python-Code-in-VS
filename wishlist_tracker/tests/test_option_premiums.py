# test_option_premiums.py
# Unit tests for option premium logic

def test_is_excellent_premium():
    from ..utils.price_analysis import is_excellent_premium
    assert is_excellent_premium(2, 60, 50, 80) == True
    assert is_excellent_premium(0.5, 60, 50, 80) == False
    assert is_excellent_premium(2, 40, 50, 80) == False
    assert is_excellent_premium(2, 90, 50, 80) == False
