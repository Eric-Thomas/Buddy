from geopy.geocoders import Nominatim
import csv

geolocator = Nominatim(user_agent='Buddy', format_string="%s, Columbus OH")

crime_addresses = []
crime_coordinates = []
crime_file = open("crimes.txt", "a")

filepath = 'crimes.txt'
with open(filepath) as fp:
    line = fp.readline()
    while line:
        line = fp.readline()
        if line:
            latitude = float(line.split()[0])
            longitude = float(line.split()[1])
            crime_coordinates.append((latitude, longitude))

def point_danger(coordinates):
    danger = 0
    for crime in crime_coordinates:
        d = (coordinates['lng'] - crime[0])**2 + (coordinates['lat'] - crime[1])**2
        # 364320 feet per degree (double check this)
        # if d < (5280 * 5 / 364320)**2: # only check crimes that occured within 5 miles
        d = 1 / d # inverse square distance penalizes closer crimes
        danger += d
    return danger

def route_danger(route, length):
    i = 0
    while len(route) < length:
        route.append(route[i])
        i += 1
    danger = 0
    for point in route:
        danger += point_danger(point)
    return danger