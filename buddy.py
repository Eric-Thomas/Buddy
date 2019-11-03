from flask import Flask, request, render_template
import requests
import json
import danger
import random


key = 'D2ZCny0cmDMUDUbsavWda8qvTD9K3iRV'
app = Flask(__name__)

@app.route('/directions', methods=['POST'])
def get_directions():
    start = request.form['start']
    end = request.form['end']
    params = {'key': key, 'from': start, 'to': end, 'routeType': 'pedestrian', 'maxRoutes': 5, 'timeOverage': 200}
    content = requests.post('http://www.mapquestapi.com/directions/v2/alternateroutes', params=params).content
    parsed_json = json.loads(content)

    resp = {'directions': [], 'turns': [], 'alternateRoutes': [], 'from': start, 'to': end, 'crimeRating': None, 'realTime': None, 'distance': None}
    turns = []
    distance = 0
    for leg in parsed_json['route']['legs']:
        for maneuver in leg['maneuvers']:
            data = {'narrative': '', 'distance': '', 'startPoint': ''}
            data['narrative'] = maneuver['narrative']
            data['distance'] = format_distance(maneuver['distance'])
            distance += maneuver['distance']
            data['startPoint'] = maneuver['startPoint']
            turns.append(maneuver['startPoint'])
            resp['directions'].append(data)

    resp['realTime'] = '%.0f' % (parsed_json['route']['realTime']/60)
    resp['crimeRating'] = '%.2f' % (danger.route_danger(turns, 0) * 10)
    resp['distance'] = '%.1f' % distance
    resp['turns'] = turns

    distance = 0
    i = 0
    if 'alternateRoutes' in parsed_json['route']:
        for alt_route in parsed_json['route']['alternateRoutes']:
            turns = []
            route = []
            for leg in alt_route['route']['legs']:
                for maneuver in leg['maneuvers']:
                    data = {'narrative': '', 'distance': '', 'startPoint': ''}
                    data['narrative'] = maneuver['narrative']
                    data['distance'] = format_distance(maneuver['distance'])
                    data['startPoint'] = maneuver['startPoint']
                    turns.append(maneuver['startPoint'])
                    route.append(data)
            resp['alternateRoutes'][i]['directions'].append(route)
            resp['alternateRoutes'][i]['crimeRating'] = '%.2f' % (danger.route_danger(turns, 0) * 10)
            resp['alternateRoutes'][i]['realTime'] = '%.0f' % (alt_route['route']['realTime']/60)
            resp['alternateRoutes'][i]['distance'] = '%0.1f' % distance
            resp['alternateRoutes'][i]['turns'] = turns
            distance += maneuver['distance']
            i += 1

    while len(resp['alternateRoutes']) < 3:
        resp['alternateRoutes'].append(get_more_routes(start, end, get_midpoint(resp)))

    lengths = [len(resp['directions'])] + [len(alt['directions']) for alt in resp['alternateRoutes']]
    max_length = max(lengths)
    resp['crimeRating'] = danger.route_danger(resp['turns'], max_length)
    print(resp.keys())
    print(resp['alternateRoutes'][0].keys())
    for i in range(3):
        resp['alternateRoutes'][i]['crimeRating'] = danger.route_danger(resp['alternateRoutes'][i]['turns'], max_length)

    get_map(start, end)
    return render_template('directions.html', result = resp)

@app.route('/')
def index():
    return render_template('index.html')

def get_more_routes(start, end, midpoint):
    midpoint = random_move_from_midpoint(midpoint)
    midpoint_str = str(midpoint['lat']) + ", " + str(midpoint['lng'])
    params = {'key': key, 'from': start, 'to': midpoint_str, 'routeType': 'pedestrian'}
    content = requests.post('http://www.mapquestapi.com/directions/v2/route', params=params).content
    parsed_json = json.loads(content)
    resp = {'directions': [[]], 'crimeRating': None, 'realTime': None, 'turns': []}
    turns = []
    distance = 0
    for leg in parsed_json['route']['legs']:
        for maneuver in leg['maneuvers']:
            data = {'narrative': '', 'distance': '', 'startPoint': ''}
            data['narrative'] = maneuver['narrative']
            data['distance'] = format_distance(maneuver['distance'])
            distance += maneuver['distance']
            data['startPoint'] = maneuver['startPoint']
            turns.append(maneuver['startPoint'])
            resp['directions'][0].append(data)
    
    resp['realTime'] = parsed_json['route']['realTime']

    params = {'key': key, 'from': midpoint_str, 'to': end, 'routeType': 'pedestrian'}
    content = requests.post('http://www.mapquestapi.com/directions/v2/route', params=params).content
    parsed_json = json.loads(content)

    for leg in parsed_json['route']['legs']:
        for maneuver in leg['maneuvers'][1:]:
            data = {'narrative': '', 'distance': '', 'startPoint': ''}
            data['narrative'] = maneuver['narrative']
            data['distance'] = format_distance(maneuver['distance'])
            distance += maneuver['distance']
            data['startPoint'] = maneuver['startPoint']
            turns.append(maneuver['startPoint'])
            resp['directions'][0].append(data)

    resp['realTime'] = '%.0f' % ((resp['realTime'] + parsed_json['route']['realTime'])/60)
    resp['crimeRating'] = '%.2f' % (danger.route_danger(turns, 0) * 10)
    resp['distance'] = '%0.1f' % distance
    resp['turns'] = turns

    return resp

def get_midpoint(resp):
    start = resp['directions'][0]['startPoint']
    end = resp['directions'][len(resp['directions'])-1]['startPoint']
    midpoint = {}
    midpoint['lng'] = (end['lng'] + start['lng'])/2
    midpoint['lat'] = (end['lat'] + start['lat'])/2
    return midpoint

def random_move_from_midpoint(midpoint):
    midpoint['lng'] += random.uniform(-0.005, 0.005)
    midpoint['lat'] += random.uniform(-0.005, 0.005)
    return midpoint

def get_map(start, end):
    params = {'key': key, 'size': '600, 400', 'start': start, 'end': end}
    res = requests.get('https://www.mapquestapi.com/staticmap/v5/map', params=params).content
    image = open("static/img/map.jpg", "wb")
    image.write(res)

def get_map_markers(directions, start, end):
    coords = get_coordinates(directions)
    locations_param = ''
    for cord in coords[:len(coords)]:
        locations_param += str(cord)+'||'
    locations_param += coords[len(coords) - 1]
    params = {'key': key, 'locations': locations_param, 'size': '600, 400', 'start': start, 'end': end}
    return requests.get('https://www.mapquestapi.com/staticmap/v5/map', params=params).content

def get_coordinates(directions):
    coords = []
    for direction in directions:
        lat_and_long = direction['startPoint']
        coords.append(str(lat_and_long['lat']) + ', ' + str(lat_and_long['lng']))

    return coords

def format_distance(distance):
    if distance < 0.1:
        distance = distance * 5280
        distance = '%0.f' % distance
        return str(distance) + " feet"
    else:
        distance = '%0.1f' % distance
        return str(distance) + ' miles'

if __name__ == '__main__':
   app.run(debug=True)
