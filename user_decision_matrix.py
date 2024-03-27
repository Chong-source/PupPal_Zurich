"""A decision matrix that takes user's preferences based on
1. Affectionate with family scale of 1 - 5
2. Good with young children scale of 1 - 5
...
Did data cleaning to delete the irrelevant columns from CSV file
"""
import csv
from dataclasses import dataclass


@dataclass
class DogBreed:
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


def dog_breed_data_loader(file: str) -> list[DogBreed]:
    """Loads the data from the breed_traits.csv file, creates a list of DogBreed objects"""
    with open(file) as dog_breed_file:
        dog_breed_file.readline()
        breed_informations = []
        dog_breed_rows = csv.reader(dog_breed_file)
        for row in dog_breed_rows:
            breed_informations.append(DogBreed(row[0], int(row[1]), int(row[2]), int(row[3]), int(row[4]), int(row[5]),
                                               int(row[6]), int(row[7]), int(row[8]), int(row[9]), int(row[10]),
                                               int(row[11]), int(row[12])))
        return breed_informations


def decision_matrix(dog_breeds: list[DogBreed],
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
                    ):
    """Returns the top 5 dogs based on the weighted criterons"""
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
    return breed_scores[:5]


if __name__ == '__main__':
    dog_breeds = dog_breed_data_loader('data/breed_traits.csv')

    print('Please give a weight to the following criteria from a scale of 1 to 5. \n'
          'Rate the criteria based off of how important it is to you.')
    waffectionate_w_family: int = int(input('Affectionate with family '))  # positive trait
    wgood_w_young_children: int = int(input('Good with young children '))  # positive trait
    wgood_w_other_dog: int = int(input('Good with other dog '))  # positive trait
    wshedding_level: int = -1 * int(input("Shedding level (1 = I don't mind shedding) (5 = Shedding is a problem) "))
    wopenness_to_strangers: int = int(input('Open to strangers '))  # positive trait
    wplayfulness: int = int(input('High in Playfulness '))  # positive
    wprotective_nature: int = int(input('High in Protective Nature '))  # positive
    wadaptability: int = int(input('High in Adaptability '))  # positive
    wtrainability: int = int(input('High in Trainability '))  # positive
    wenergy: int = int(input('High Energy level '))  # Positive
    bark_decide = input("Is high amount of barking considered a positive or "
                        "negative trait (positive or negative) ")
    result = (lambda bark_decide: 1 if bark_decide == 'positive' else -1)(bark_decide)
    wbarking: int = result * int(input("How important is this criterion? "))
    stimulation_decide = input("Is needing lots of attention considered a positive or "
                               "negative trait (positive or negative) ")
    result = (lambda stimulation_decide: 1 if stimulation_decide == 'positive' else -1)(stimulation_decide)
    wstimulation_needs: int = result * int(input("How important is this criterion?  "))  # Let users decide

    top_5_dogs = decision_matrix(dog_breeds,
                                 waffectionate_w_family,
                                 wgood_w_young_children,
                                 wgood_w_other_dog,
                                 wshedding_level,
                                 wopenness_to_strangers,
                                 wplayfulness,
                                 wprotective_nature,
                                 wadaptability,
                                 wtrainability,
                                 wenergy,
                                 wbarking,
                                 wstimulation_needs)

    print('The top 5 dogs matching your criterions are:')
    for dog in top_5_dogs:
        print(dog[0].replace("\xa0", ' '))
