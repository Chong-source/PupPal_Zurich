"""Loads data from the Zurich dog data files into a graph.
"""
import csv
import math
from dataclasses import dataclass

from districts import District
from graphs import Graph
from userdata import User


@dataclass
class UserPreferenceDogBreed:
    """A class of dog breed that stores information about each breed that stores the dog's rating
    of each trait based off of the data collected by the american Kennel Club:
    https://www.kaggle.com/datasets/sujaykapadnis/dog-breeds"""
    breed_name: str
    affectionate_w_family: int  # positive trait
    good_w_young_children: int  # positive trait
    good_w_other_dog: int  # positive trait
    shedding_level: int  # do negative weight -> negative trait
    openness_to_strangers: int  # positive trait
    playfulness: int  # positive
    protective_nature: int  # positive
    adaptability: int  # positive
    trainability: int  # positive
    energy: int  # Let users decide
    barking: int  # negative trait
    stimulation_needs: int  # Let users decide


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
            if not raw_age_range.strip():
                continue  # Missing age range
            gender = row[2].upper()
            if not gender.strip():
                continue  # Missing gender data
            district_id = int(row[4])
            if district_id not in district_mapping:
                continue  # Invalid district ID
            district = district_mapping[district_id]
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


def get_raw_district_distances(
        districts: set[District],
        district_distance_file: str
) -> dict[District, dict[District, float]]:
    """Takes existing district data and creates a mapping between districts and their distance
    to every other district by loading data from the CSV file at district_distance_file.

    Raw data in this context means it has not been normalized (and remains in kilometers,
    not bounded by 0.0 and 1.0)
    """
    district_lookup = {district.district_id: district for district in districts}
    raw_district_distances = {}
    with open(district_distance_file) as district_distance_content:
        reader = csv.reader(district_distance_content)
        next(reader, None)
        for row in reader:
            district_id = row[0]
            origin = district_lookup[int(district_id)]
            if not origin:
                continue
            district_distances = {}
            district_mapping_raw = row[1].split('|')
            for mapping in district_mapping_raw:
                mapping_split = mapping.split(':')
                destination_id, distance = int(mapping_split[0]), float(mapping_split[1])
                destination = district_lookup[destination_id]
                if not destination or destination == origin:
                    continue
                district_distances[destination] = distance
            raw_district_distances[origin] = district_distances
    return raw_district_distances


def normalize_district_distances(raw_district_distances: dict[District, dict[District, float]]) -> None:
    """Normalize district distances so that all of them are between 0.0 and 1.0 (from raw km data).
    In this case, also flips the values so that 1.0 indicates close districts and 0.0 is far.
    Mutates the given dictionary.
    """
    min_distance = math.inf
    max_distance = 0
    for origin in raw_district_distances:
        for destination in raw_district_distances[origin]:
            assert origin != destination
            distance = raw_district_distances[origin][destination]
            min_distance = min(distance, min_distance)
            max_distance = max(distance, max_distance)
    if max_distance == 0:
        raise ValueError
    difference = max_distance - min_distance
    for origin in raw_district_distances:
        for destination in raw_district_distances[origin]:
            distance = raw_district_distances[origin][destination]
            distance -= min_distance
            distance /= difference
            distance = 1 - distance
            raw_district_distances[origin][destination] = distance
            assert 0.0 <= distance <= 1.0


def apply_district_distances(district_distances: dict[District, dict[District, float]]) -> None:
    """Mutates the distance attributes of each district in the district_distances dictionary
    so that it has the distance values corresponding to our given dictionary.
    """
    for origin in district_distances:
        for destination in district_distances[origin]:
            assert origin != destination
            origin.set_distance(destination, district_distances[origin][destination])


def dog_breed_data_loader(file: str) -> list[UserPreferenceDogBreed]:
    """Loads the data from the breed_traits.csv file, creates a list of DogBreed objects"""
    with open(file) as dog_breed_file:
        dog_breed_file.readline()
        breed_informations = []
        dog_breed_rows = csv.reader(dog_breed_file)
        for row in dog_breed_rows:
            breed_informations.append(
                UserPreferenceDogBreed(row[0], int(row[1]), int(row[2]), int(row[3]), int(row[4]), int(row[5]),
                                       int(row[6]), int(row[7]), int(row[8]), int(row[9]), int(row[10]),
                                       int(row[11]), int(row[12])))
        return breed_informations
