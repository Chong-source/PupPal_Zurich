"""Contains functions for determining the distance between two districts.
Uses the Google Maps API.
"""
from districts import District
import requests
import os.path


def load_district_distance(api_key: str, origin: District, destination: District) -> float:
    """Uses the Google Maps API to load the distance between two districts (in kilometers of driving).

    Must provide a valid GCP API key for using Maps.
    Should be called asynchronously (awaits endpoint response).
    """
    endpoint_url = (f'https://maps.googleapis.com/maps/api/distancematrix/json'
                    f'?destinations={destination.district_name}'
                    f'&origins={origin.district_name}'
                    f'&units=metric'
                    f'&key={api_key}')
    response = requests.get(endpoint_url)
    distance = float(response.json()['rows'][0]['elements'][0]['distance']['text'][:-3])
    return distance


def create_distance_csv(api_key: str, csv_path: str, districts: set[District]) -> None:
    """Creates a CSV file at the given path that will contain one row for each district,
    and then on each row a mapping between district IDs and distance to each district.

    Such a row looks like this: 100,123:1.1|456:2.5|etc
    Where 100 is the district ID, 123 and 456 are district IDs of close districts,
    and 1.1 and 2.5 are distances to these districts.

    This makes len(destinations) ** 2 API calls, use it wisely.

    The csv_path file must not already exist.
    """
    if os.path.isfile(csv_path):
        raise FileExistsError  # File must not exist!
    with open(csv_path, 'w') as csv_file:
        csv_file.write('district_id,district_distances\n')  # header
        for origin in districts:
            district_distances = ''
            for destination in districts:
                if origin == destination:
                    continue
                distance = load_district_distance(api_key, origin, destination)
                district_distances += f'{destination.district_id}:{distance}|'
            district_distances = district_distances[:-1]  # Remove last |
            csv_file.write(f'{origin.district_id},{district_distances}\n')
