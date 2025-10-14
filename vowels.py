def count_vowels(text: str) -> int:
    vowels = "aeiouyąęó"
    return sum(1 for c in text.lower() if c in vowels)
