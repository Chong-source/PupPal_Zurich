"""Loads data from the Zurich dog data files into a graph.
"""
import csv

from csc111.assignments.project2.districts import District
from csc111.assignments.project2.graphs import Graph
from csc111.assignments.project2.userdata import AgeRange, User


def load_dog_data(dog_data_file: str, districts: set[District]) -> Graph:
    """Creates a graph containing every user in the given dog data file,
    and every dog breed with edges between owners and pets.

    Ignores Mischling/mixed-breed dogs.
    """
    graph = Graph()
    district_mapping = {district.district_id: district for district in districts}
    users = {}
    with (open(dog_data_file) as dog_data_content):
        first_line = True
        for row in csv.reader(dog_data_content):
            if first_line:  # Skip the first line header
                first_line = False
                continue
            user_id = int(row[0])
            raw_age_range = row[1]
            gender = row[2].upper()
            district = district_mapping[int(row[4])]
            dog_breed = row[5].capitalize()
            if 'Mischling' in dog_breed:  # Ignore mix-breed dogs because its complicated
                continue
            split_age_range = raw_age_range.split('-')
            age_range = AgeRange(int(split_age_range[0]), int(split_age_range[1]))
            if user_id not in district_mapping:
                users[user_id] = User(user_id, age_range, gender, district)
                graph.add_vertex(users[user_id])
            user = users[user_id]
            graph.add_vertex(dog_breed)
            graph.add_edge(dog_breed, user)
    return graph


def load_district_data(district_data_file: str) -> set[District]:
    """Loads the set of districts from a given district data file,
    that contains each district's name and ID number.
    """
    # TODO
