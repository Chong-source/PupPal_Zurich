"""A graph representing how close the districts are to each other
"""


if __name__ == '__main__':
    # Getting the location for
    import requests
    key = input("API Key: ")
    url = (f"https://maps.googleapis.com/maps/api/distancematrix/json"
           f"?destinations=Enge"
           f"&origins=Alt-Wiedikon"
           f"&units=metric"
           f"&key={key}")
    response = requests.get(url)
    distance = float(response.json()['rows'][0]['elements'][0]['distance']['text'][:-3])
