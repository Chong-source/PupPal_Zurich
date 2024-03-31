"""Class that processes information about various districts.

Primarily used to hold data about districts (such as their IDs and their names)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class District:
    """Represents a district in Zurich.

    Instance Attributes:
        - district_id: the numerical ID (from 1 to 123) of this district (quartier) which is 1 of 34.
        - district_name: the human-readable name of this district (if you speak swiss german)
        - district_distances: map to other districts with how far apart they are. Empty if not initialized.
                Each one stores a value from 0.0 to 1.0 depending on how close they are.
    """
    district_id: int
    district_name: str
    __district_distances: Optional[dict[District, float]] = None

    def __hash__(self):
        return hash(str(self.district_id))

    def get_distance(self, other: District) -> float:
        """Gets the cached distance from this district to another on a scale from 0.0 to 1.0.
        Performs no calculations itself, must be added to this object by another method.
        Returns 1.0 if the other district is this district.

        Raises RuntimeError if other does not exist in this district's district_distances.
        """
        if other == self:
            return 1.0
        if not self.__district_distances or other not in self.__district_distances:
            raise RuntimeError
        return self.__district_distances[other]

    def set_distance(self, other: District, distance: float):
        """Caches the distance between this district and another district for use later on.
        """
        if not self.__district_distances:
            self.__district_distances = {}
        self.__district_distances[other] = distance
