import sys
import math
from io import BytesIO
import requests
from PIL import Image
from get_delta import get_spn


def lonlat_distance(a, b):

    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b

    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    distance = math.sqrt(dx * dx + dy * dy)

    return distance


toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

json_response = response.json()
toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
toponym_coodrinates = toponym["Point"]["pos"]
toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

delta = str(get_spn(toponym_to_find) + 0.015)

search_api_server = "https://search-maps.yandex.ru/v1/"
search_params = {
    "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
    "text": "аптека",
    "lang": "ru_RU",
    "ll": ','.join(toponym_coodrinates.split()),
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)
if not response:
    print('Ошибка при запросе изображения!')
    exit(0)

json_response = response.json()
organization = json_response["features"][0]
point = ','.join(str(i) for i in organization["geometry"]["coordinates"])
map_params = {
    "ll": ",".join([toponym_longitude, toponym_lattitude]),
    "spn": ",".join([delta, delta]),
    "l": "map",
    "pt": f"{point},flag~{','.join(toponym_coodrinates.split())}"
}
map_api_server = "http://static-maps.yandex.ru/1.x/"
response = requests.get(map_api_server, params=map_params)

Image.open(BytesIO(
    response.content)).show()

org_address = organization["properties"]["CompanyMetaData"]["address"]
org_name = organization["properties"]["CompanyMetaData"]["name"]
org_phone = organization["properties"]["CompanyMetaData"]["Phones"][0]["formatted"]
print(org_address)
print(org_name)
print(org_phone)
print(int(lonlat_distance([float(i) for i in point.split(',')], [float(i) for i in toponym_coodrinates.split()])), 'м')

