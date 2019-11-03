from flask import Flask, request, render_template
import requests
import json
import danger


key = 'D2ZCny0cmDMUDUbsavWda8qvTD9K3iRV'
app = Flask(__name__)

@app.route('/directions', methods=['POST'])
def get_directions():
    start = request.form['start']
    end = request.form['end']
    params = {'key': key, 'from': start, 'to': end, 'routeType': 'pedestrian', 'maxRoutes': 5, 'timeOverage': 200}
    content = requests.post('http://www.mapquestapi.com/directions/v2/alternateroutes', params=params).content
    parsed_json = json.loads(content)
    resp = {'directions': [], 'alternateRoutes': [{'directions': [], 'crimeRating': None}], 'from': start, 'to': end, 'crimeRating': None}
    turns = []
    for leg in parsed_json['route']['legs']:
        for maneuver in leg['maneuvers']:
            data = {'narrative': '', 'distance': '', 'startPoint': ''}
            data['narrative'] = maneuver['narrative']
            data['distance'] = maneuver['distance']
            data['startPoint'] = maneuver['startPoint']
            turns.append(maneuver['startPoint'])
            resp['directions'].append(data)

    resp['crimeRating'] = danger.route_danger(turns)


    i = 0
    try:
        for alt_route in parsed_json['route']['alternateRoutes']:
            turns = []
            route = []
            for leg in alt_route['route']['legs']:
                for maneuver in leg['maneuvers']:
                    data = {'narrative': '', 'distance': '', 'startPoint': ''}
                    data['narrative'] = maneuver['narrative']
                    data['distance'] = maneuver['distance']
                    data['startPoint'] = maneuver['startPoint']
                    turns.append(maneuver['startPoint'])
                    route.append(data)
            resp['alternateRoutes'][i]['directions'].append(route)
            resp['alternateRoutes'][i]['crimeRating'] = danger.route_danger(turns)
            i += 1
    except Exception as e:
        print("exception: " + str(e))

    return render_template('directions.html', result = resp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
   app.run(debug=True)
