"""Loads data from the Zurich dog data files into a graph.
"""
import csv

from districts import District
from graphs import Graph
from userdata import User


def load_dog_data(dog_data_file: str, districts: set[District]) -> Graph:
    """Creates a graph containing every user in the given dog data file,
    and every dog breed with edges between owners and pets.

    Ignores Mischling/mixed-breed dogs.
    """
    graph = Graph()
    district_mapping = {district.district_id: district for district in districts}
    users = {}
    with (open(dog_data_file) as dog_data_content):
        reader = csv.reader(dog_data_content)
        next(reader, None)  # Skip the first line header
        for row in reader:
            user_id = int(row[0])
            raw_age_range = row[1]
            gender = row[2].upper()
            district = district_mapping[int(row[4])]
            dog_breed = row[5].capitalize()
            if 'Mischling' in dog_breed:  # Ignore mix-breed dogs because its complicated
                continue
            split_age_range = raw_age_range.split('-')
            age = (int(split_age_range[0]) + int(split_age_range[1])) // 2  # Average in age range
            if user_id not in district_mapping:
                users[user_id] = User(user_id, age, gender, district)
                graph.add_vertex(users[user_id])
            user = users[user_id]
            graph.add_vertex(dog_breed)
            graph.add_edge(dog_breed, user)
    return graph


def load_district_data(district_data_file: str) -> set[District]:
    """Loads the set of districts from a given district data file,
    that contains each district's name and ID number.
    """
    with open(district_data_file) as districts_data:
        reader = csv.reader(districts_data)
        districts = set()
        next(reader, None)
        for row in reader:
            # Sample row: ['261031', '31', 'Alt-Wiedikon', '261', '169']
            district = District(int(row[1]), row[2])
            districts.add(district)
        return districts


def add_district_distances(districts: set[District], district_distance_file: str) -> None:
    """Takes existing district data and mutates it with the distances to every other district.

    Loads data from the CSV file at district_distance_file.
    """
    district_lookup = {district.district_id: district for district in districts}
    with open(district_distance_file) as district_distance_content:
        reader = csv.reader(district_distance_content)
        next(reader, None)
        for row in reader:
            district_id = row[0]
            origin = district_lookup[int(district_id)]
            if not origin:
                continue
            district_mapping_raw = row[1].split('|')
            for mapping in district_mapping_raw:
                mapping_split = mapping.split(':')
                destination_id, distance = int(mapping_split[0]), float(mapping_split[1])
                destination = district_lookup[destination_id]
                if not destination:
                    continue
                origin.set_distance(destination, distance)
