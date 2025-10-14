from vowels import count_vowels

def test_count_vowels():
    assert count_vowels("Python") == 1
    assert count_vowels("AEIOUY") == 6
    assert count_vowels("bcd") == 0
    assert count_vowels("") == 0
    assert count_vowels("Próba żółwia") == 4
