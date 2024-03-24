"""Class that is used to compare how similar one user is to another user.
"""
from __future__ import annotations

from dataclasses import dataclass

from districts import District


@dataclass
class AgeRange:
    """Represents a range of ages (that a user can fall in).

    Instance Attributes:
        - min_age: minimum age of this age range
        - max_age: maximum age of this age range

    Representation Invariants:
        - 0 <= min_age <= max_age
    """
    min_age: int
    max_age: int


class User:
    """A user class that represents a dog owner or potential dog owner.
    Used to compare similarity between two users for recommendations.

    Representation Invariants:
        - gender in {'F', 'M', 'O'}
    """
    user_id: int
    age_range: AgeRange
    gender: str
    district: District

    def __init__(self, user_id: int, age_range: AgeRange, gender: str, district: District):
        """Create a user with a given user_id, age_range, gender, and district.

        Preconditions:
            - gender in {'F', 'M', 'O'}
        """
        self.user_id = user_id
        self.age_range = age_range
        self.gender = gender
        self.district = district

    def compare(self, other: User) -> float:
        """Gives a numerical score from 0.0 to 1.0 on how similar this user is to a given user
        Uses age range, gender, and city district to determine.

        Preconditions:
            - other.user_id != self.user_id
        """
        # TODO
