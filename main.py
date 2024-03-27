"""Main file for our CSC111 Project 2.
"""
import data_loader
from userdata import User

if __name__ == '__main__':
    districts = data_loader.load_district_data('data/district_quarters_2017.csv')
    district_data_dict = data_loader.get_raw_district_distances(districts, 'data/district_closeness_2017.csv')
    data_loader.normalize_district_distances(district_data_dict)
    data_loader.apply_district_distances(district_data_dict)
    district_data = set(district_data_dict.keys())
    dog_graph = data_loader.load_dog_data('data/zurich_dog_data_2017.csv', district_data)
    district_lookup = {district.district_id: district for district in district_data}

    age = int(input('User age: '))
    gender = input('User gender (f/m/o): ').upper()
    district = district_lookup[int(input('User district: '))]
    limit = int(input('Number of recommendations: '))
    input_user = User(-1, age, gender, district)

    dog_breeds = {node for node in dog_graph.get_all_nodes() if not isinstance(node, User)}
    dog_breed_score = {}
    for dog_breed in dog_breeds:
        user_owners: set[User] = dog_graph.get_neighbours(dog_breed)
        # +8 and +10 makes it so that greater average is given to dogs with more samples
        average_similarity = (sum([user.compare(input_user) for user in user_owners]) + 8) / (len(user_owners) + 10)
        dog_breed_score[dog_breed] = average_similarity
    # for dog_breed in dog_breeds:
    #     print(f'{dog_breed}, count: {len(dog_graph.get_neighbours(dog_breed))}')
    dog_breed_score_clone = dog_breed_score.copy()
    top_matches = []
    while len(top_matches) < limit:
        max_score = -1
        max_breed = ''
        for dog_breed in dog_breed_score:
            if dog_breed_score[dog_breed] > max_score:
                max_score = dog_breed_score[dog_breed]
                max_breed = dog_breed
        top_matches.append(max_breed)
        dog_breed_score.pop(max_breed)

    print('Top breeds:')
    for match in top_matches:
        print(f'  - {match}, score: {dog_breed_score_clone[match]}')
