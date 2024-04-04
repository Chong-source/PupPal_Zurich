"""A file that generates the data using Google's Custom Search API and Google Translate.
Creates CSV data on translation of dog breed names from German to English, and
finds links to images of different dog breeds for displaying to the user.
"""
import csv
from googletrans import Translator

import requests
import json


def dog_breed_names_csv_writer(dog_data_file: str, new_file_path: str) -> None:
    """Creates a csv file in the format
    <German Dog Breed Name>,<English Dog Breed Name>

    Representation Invariants:
    - dog_data_file: must be in the data folder
    """
    translator = Translator()
    dog_breeds = set()

    with open(dog_data_file) as dog_data_content:
        reader = csv.reader(dog_data_content)
        next(reader, None)  # Skip the first line header
        i = 0
        for row in reader:
            if 'Mischling' == row[5].capitalize():  # Ignore mix-breed dogs because its complicated
                continue
            else:
                dog_breed = row[5].capitalize()
                print(i)
                i += 1
                dog_breeds.add(dog_breed)

    with open(new_file_path, 'w') as new_file:
        csv_writer = csv.writer(new_file)
        csv_writer.writerow(['German Dog Breed Name', 'English Dog Breed Name'])
        print('here')
        for breed in dog_breeds:
            try:
                translated = translator.translate(text=breed, src='de', dest='en')
            except (AttributeError, TimeoutError):
                continue
            csv_writer.writerow([breed, translated.text.capitalize()])
            print('row added')


def create_dog_image_csv(dog_names_file: str, new_file_path: str, api: str, cse: str) -> None:
    """A method that creates a new csv document based on the dog_file and
        creates the new file using new_file_path

    Representation Invariants:
    - dog_names_file: must be in the data folder
    - new_file_path: must be a path that creates a file in the data folder
    - The API code must be valid
    - The CSE (Custom Search Engine) code must be valid
    """
    dog_names = []
    with open(dog_names_file) as file:
        file.readline()  # skips the first line
        reader = csv.reader(file)
        for row in reader:
            dog_names.append(row[1])

    with open(new_file_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['dog_name', 'image_url'])
        count = 2
        for breed in dog_names:
            url = (f"https://www.googleapis.com/customsearch/v1?"
                   f"key={api_key}&"
                   f"cx={cse_id}&"
                   f"searchType=image&"
                   f"q={breed}")
            response = requests.get(url)
            data = json.loads(response.text)

            if 'items' in data:
                # Get Url of the first image
                image_url = data['items'][0]['link']
                writer.writerow([breed, image_url])
                count += 1
            else:
                print(f'{breed}, {count}')
                count += 1
                continue


def data_cleaning(file1: str, file2: str, unduplicated: str) -> None:
    """A function that ignores the duplicated rows from the second file compared to file1 and creates a
    new file without the duplicates.
    """
    dog_breeds = set()
    with open(file1) as file1:
        reader = csv.reader(file1)
        for row in reader:
            dog_breeds.add(row[0])

    with open(unduplicated, 'w') as unduplicated:
        writer = csv.writer(unduplicated)
        with open(file2) as file2:
            reader = csv.reader(file2)
            for row in reader:
                if not (row[0] in dog_breeds):
                    print(row[0])
                    writer.writerow(row)


# if __name__ == '__main__':
    # api_key = input("API_key: ")
    # cse_id = input("CSE_id: ")
    # create_dog_image_csv('data/translated_dog_breed.csv',
    #                      'data/dog_images4.csv',
    #                      api_key,
    #                      cse_id)

    # data_cleaning('data/dog_images3.csv', 'data/dog_images4.csv',
    #               'data/no_duplicates.csv')
