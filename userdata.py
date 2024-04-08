"""
© Copyright 2024 Kai Lo and Chong Wan
Class that is used to compare how similar one user is to another user.

Does not load data, primarily used for calculating user similarity though.
"""
from __future__ import annotations
from districts import District


class User:
    """A user class that represents a dog owner or potential dog owner.
    Used to compare similarity between two users for recommendations.

    Representation Invariants:
        - gender in {'F', 'M', 'O'}
    """
    user_id: int
    age: int
    gender: str
    district: District

    def __init__(self, user_id: int, age: int, gender: str, district: District) -> None:
        """Create a user with a given user_id, age, gender, and district.

        Preconditions:
            - gender in {'F', 'M', 'O'}
        """
        self.user_id = user_id
        self.age = age
        self.gender = gender
        self.district = district

    def compare(self, other: User) -> float:
        """Gives a numerical score from 0.0 to 1.0 on how similar this user is to a given user
        Uses age, gender, and city district to determine.

        Preconditions:
            - other.user_id != self.user_id
        """
        age_diff = abs(other.age - self.age)
        age_score = (-0.0001 * (age_diff ** 2)) + 1  # Plot -0.0001x^2+1 in desmos
        assert 0.0 <= age_score <= 1.0
        gender_score = 1.0 if self.gender in [other.gender, 'o'] else 0.5
        assert 0.0 <= gender_score <= 1.0
        district_score = self.district.get_distance(other.district)
        assert 0.0 <= district_score <= 1.0
        score = 0.4 * age_score + 0.2 * gender_score + 0.4 * district_score
        assert 0.0 <= score <= 1.0
        return score
