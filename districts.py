"""Class that processes information about various districts.

Primarily used to hold data about districts (such as their IDs and their names)
"""
from dataclasses import dataclass


@dataclass
class District:
    """Represents a district in Zurich.

    Instance Attributes:
        - district_id: the numerical ID (from 1 to 123) of this district (quartier) which is 1 of 34.
        - district_name: the human-readable name of this district (if you speak swiss german)
    """
    district_id: int
    district_name: str

    def __hash__(self):
        return hash(str(self.district_id))


def get_distance(district1: District, district2: District) -> float:
    """Uses external data/google maps API/manual data to determine how far apart two districts are.

    Returns a float from 0.0 to 1.0.
    """
    # TODO
