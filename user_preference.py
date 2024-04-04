"""File for processing user preference information and generating recommendations.

A decision matrix that takes user's preferences based on criterias
decided by the American Kennel Club.
Did data cleaning to delete the irrelevant columns/criterias from CSV file.
"""
import math

from data_loader import UserPreferenceDogBreed, dog_breed_data_loader


def get_preference_recommendations(dog_breeds: list[UserPreferenceDogBreed],
                                   limit: int,
                                   waffectionate_w_family: int,  # positive trait
                                   wgood_w_young_children: int,  # positive trait
                                   wgood_w_other_dog: int,  # positive trait
                                   wshedding_level: int,  # do negative weight -> negative trait
                                   wopenness_to_strangers: int,  # positive trait
                                   wplayfulness: int,  # positive
                                   wprotective_nature: int,  # positive
                                   wadaptability: int,  # positive
                                   wtrainability: int,  # positive
                                   wenergy: int,  # Let users decide
                                   wbarking: int,  # negative trait
                                   wstimulation_needs: int  # Let users decide
                                   ) -> list[tuple[str, int]]:
    """Returns the top 5 dogs based on the weighted criterons.

    Returns limit choices.
    """
    breed_scores = []
    for dog_breed in dog_breeds:
        breed_score = waffectionate_w_family * dog_breed.affectionate_w_family + \
                      wgood_w_young_children * dog_breed.good_w_young_children + \
                      wgood_w_other_dog * dog_breed.good_w_other_dog + \
                      wshedding_level * dog_breed.shedding_level + \
                      wopenness_to_strangers * dog_breed.openness_to_strangers + \
                      wplayfulness * dog_breed.playfulness + \
                      wprotective_nature * dog_breed.protective_nature + \
                      wadaptability * dog_breed.adaptability + \
                      wtrainability * dog_breed.trainability + \
                      wenergy * dog_breed.energy + \
                      wbarking * dog_breed.barking + \
                      wstimulation_needs * dog_breed.stimulation_needs
        breed_scores.append((dog_breed.breed_name, breed_score))
        breed_scores.sort(key=lambda key: key[1], reverse=True)
    return breed_scores[:limit]


def weight_raw_preference_data(affectionate_w_family: int,
                               good_w_young_children: int,
                               good_w_other_dog: int,
                               shedding_level: int,
                               open_to_strangers: int,
                               playfulness: int,
                               protective_nature: int,
                               adaptability: int,
                               trainability: int,
                               energy: int,
                               bark_decide: str,
                               bark_important: int,
                               stimulation_decide: str,
                               stimulation_important: int
                               ) -> tuple[int, int, int, int, int, int, int, int, int, int, int, int]:
    """Takes raw user data on dog preference and adapts it to fit our data set.
    """
    return (
        affectionate_w_family,
        good_w_young_children,
        good_w_other_dog,
        shedding_level * -1,
        open_to_strangers,
        playfulness,
        protective_nature,
        adaptability,
        trainability,
        energy,
        (1 if bark_decide == 'positive' else -1) * bark_important,
        (1 if stimulation_decide == 'positive' else -1) * stimulation_important
    )


def normalize_preference_recommendations(scores: list[tuple[str, int]]) -> list[tuple[str, float]]:
    """Turns raw dog breed recommendations (with scores that are uncapped) into normalized (0.0 to 1.0).
    scores is a list of dog breeds where the first part of the tuple is the name and the second part is the score.
    """
    normal_scores = []
    min_score = math.inf
    max_score = -math.inf
    for score in scores:
        if score[1] < min_score:
            min_score = score[1]
        if score[1] > max_score:
            max_score = score[1]
    max_score += (max_score - min_score)
    min_score = max_score - (max_score - min_score) * 2
    for score in scores:
        normalized = score[1] - min_score
        normalized /= max_score - min_score
        normal_scores.append((score[0], normalized))
    return normal_scores


if __name__ == '__main__':
    breeds = dog_breed_data_loader('data/breed_traits.csv')

    print('Please give a weight to the following criteria from a scale of 1 to 5. \n'
          'Rate the criteria based off of how important it is to you.')
    weighted = weight_raw_preference_data(
        int(input('Affectionate with family ')),
        int(input('Good with young children ')),
        int(input('Good with other dog ')),
        int(input("Shedding level (1 = I don't mind shedding) (5 = Shedding is a problem) ")),
        int(input('Open to strangers ')),
        int(input('High in Playfulness ')),
        int(input('High in Protective Nature ')),
        int(input('High in Adaptability ')),
        int(input('High in Trainability ')),
        int(input('High Energy level ')),
        input("Is high amount of barking considered a positive or "
              "negative trait (positive or negative) "),
        int(input("How important is this criterion? ")),
        input("Is needing lots of attention considered a positive or "
              "negative trait (positive or negative) "),
        int(input("How important is this criterion?  "))
    )
    top_5_dogs = get_preference_recommendations(breeds, 5, *weighted)
    print('The top 5 dogs matching your criterions are:')
    for dog in top_5_dogs:
        print(dog[0].replace("\xa0", ' '))
