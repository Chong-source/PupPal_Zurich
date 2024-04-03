"""File for processing user demographic information.
"""
import data_loader
from graphs import Graph
from userdata import User


def get_demographic_recommendations(input_user: User, limit: int, dog_graph: Graph) -> list[tuple[str, float]]:
    """Gets a recommendation of dog breed (names) based off of user demographics.

    Returns a list of tuples that contain the name of the dog breed [0] and the score it got [1] from 0.0 to 1.0.
    """
    dog_breeds = {node for node in dog_graph.get_all_nodes() if not isinstance(node, User)}
    dog_breed_score = {}
    for dog_breed in dog_breeds:
        user_owners: set[User] = dog_graph.get_neighbours(dog_breed)
        # +7 and +10 makes it so that greater average is given to dogs with more samples
        average_similarity = (sum([target.compare(input_user) for target in user_owners]) + 7) / (len(user_owners) + 10)
        dog_breed_score[dog_breed] = average_similarity
    top_matches = []
    while len(top_matches) < limit:
        max_score = -1
        max_breed = ''
        for dog_breed in dog_breed_score:
            if dog_breed_score[dog_breed] > max_score:
                max_score = dog_breed_score[dog_breed]
                max_breed = dog_breed
        top_matches.append((max_breed, dog_breed_score[max_breed]))
        dog_breed_score.pop(max_breed)
    return top_matches


if __name__ == '__main__':
    districts = data_loader.load_district_data('data/district_quarters_2017.csv')
    district_data_dict = data_loader.get_raw_district_distances(districts, 'data/district_closeness_2017.csv')
    data_loader.normalize_district_distances(district_data_dict)
    data_loader.apply_district_distances(district_data_dict)
    district_data = set(district_data_dict.keys())
    graph, district_graph_unused = data_loader.load_dog_data('data/zurich_dog_data_2017.csv', district_data)
    district_lookup = {district.district_id: district for district in district_data}

    age = int(input('User age: '))
    gender = input('User gender (f/m/o): ').upper()
    district = district_lookup[int(input('User district: '))]
    number_of_recommendations = int(input('Number of recommendations: '))
    user = User(-1, age, gender, district)

    for breed in get_demographic_recommendations(user, number_of_recommendations, graph):
        print(f'- {breed[0]}, score: {breed[1]}')
