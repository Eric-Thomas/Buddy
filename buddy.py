from flask import Flask, request, render_template
import requests
import json
import pprint

key = 'D2ZCny0cmDMUDUbsavWda8qvTD9K3iRV'
app = Flask(__name__)

@app.route('/directions', methods=['POST'])
def get_directions():
    start = request.form['start']
    end = request.form['end']
    params = {'key': key, 'from': start, 'to': end, 'routeType': 'pedestrian', 'maxRoutes': 5, 'timeOverage': 200}
    content = requests.post('http://www.mapquestapi.com/directions/v2/alternateroutes', params=params).content
    parsed_json = json.loads(content)
    pp = pprint.PrettyPrinter()
    resp = {'directions': [], 'alternateRoutes': [], 'from': start, 'to': end}
    for leg in parsed_json['route']['legs']:
        for maneuver in leg['maneuvers']:
            data = {'narrative': '', 'distance': '', 'startPoint': ''}
            data['narrative'] = maneuver['narrative']
            data['distance'] = maneuver['distance']
            data['startPoint'] = maneuver['startPoint']
            resp['directions'].append(data)


    try:
        for alt_route in parsed_json['route']['alternateRoutes']:
            route = []
            for leg in alt_route['route']['legs']:
                for maneuver in leg['maneuvers']:
                    data = {'narrative': '', 'distance': '', 'startPoint': ''}
                    data['narrative'] = maneuver['narrative']
                    data['distance'] = maneuver['distance']
                    data['startPoint'] = maneuver['startPoint']
                    route.append(data)
            resp['alternateRoutes'].append(route)
    except:
        print('there are no alternate routes')

    print(resp)
    return render_template('directions.html', result = resp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
   app.run(debug=True)
