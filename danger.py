from geopy.geocoders import Nominatim
import csv

geolocator = Nominatim(user_agent='Buddy', format_string="%s, Columbus OH")

crime_addresses = []
crime_coordinates = []
crime_file = open("crimes.txt", "a")

# Load crime data
# with open('data1-107.csv') as csv_file:
#     csv_reader = csv.reader(csv_file, delimiter=',')
#     line_count = 0
#     for row in csv_reader:
#         if line_count == 0:
#             print(f'Column names are {", ".join(row)}')
#         else:
#             crime_addresses.append(row[4])
#         line_count += 1
#     print(f'Processed {line_count} lines.')

# for crime in crime_addresses[1250:]:
#     try:
#         location = geolocator.geocode(crime)
#         coordinates = (location.latitude, location.longitude)
#         crime_coordinates.append(coordinates)
#         crime_file.write(str(location.latitude) + ' ' + str(location.longitude) + '\n')
#     except Exception as e:
#         print(e)

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

def route_danger(route):
    danger = 0
    for point in route:
        danger += point_danger(point)
    return danger