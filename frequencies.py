def word_frequencies(text: str) -> dict:
    import string

    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    words = text.split()

    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    return freq
