"""5 x 5 risk matrix: score = likelihood x impact, then a rating band.

Bands match the CASE expression in sql/schema.sql:
    Low 1-4, Medium 5-9, High 10-16, Critical 20-25
"""

BANDS = [(20, "Critical"), (10, "High"), (5, "Medium"), (1, "Low")]

RATING_ORDER = ["Critical", "High", "Medium", "Low"]


def score(likelihood: int, impact: int) -> int:
    if not (1 <= likelihood <= 5 and 1 <= impact <= 5):
        raise ValueError("likelihood and impact must be between 1 and 5")
    return likelihood * impact


def rating(value: int) -> str:
    for floor, name in BANDS:
        if value >= floor:
            return name
    raise ValueError(f"score {value} is below 1")
