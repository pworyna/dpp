def calculate_discount(price: float, discount: float) -> float:
    if not 0 <= discount <= 1:
        raise ValueError("Zniżka musi być pomiędzy 0 a 1")
    return price * (1 - discount)
