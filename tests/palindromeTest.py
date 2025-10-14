import pytest
from palindrome import is_palindrome

@pytest.mark.parametrize("text, expected", [
    ("kajak", True),
    ("Kobyła ma mały bok", True),
    ("python", False),
    ("", True),
    ("A", True),
])
def test_is_palindrome(text, expected):
    assert is_palindrome(text) == expected
