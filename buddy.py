from flask import Flask, request
import requests
import json
import pprint

key = 'D2ZCny0cmDMUDUbsavWda8qvTD9K3iRV'
app = Flask(__name__)

@app.route('/directions', methods=['GET'])
def get_directions():
    # start = request.args.get('from')
    # end = request.args.get('to')
    start = '1900 Summit Street Columbus Ohio'
    end = '1494 North High Street Columbus Ohio'
    params = {'key': key, 'from': start, 'to': end, 'routeType': 'pedestrian', 'narrativeType': 'html'}
    content = requests.get('http://www.mapquestapi.com/directions/v2/route', params=params).content
    parsed_json = json.loads(content)
    pp = pprint.PrettyPrinter()
    pp.pprint(parsed_json)
    resp = {'directions': [],}
    for leg in parsed_json['route']['legs']:
        for maneuver in leg['maneuvers']:
            data = {'narrative': '', 'distance': '', 'startPoint': ''}
            data['narrative'] = maneuver['narrative']
            data['distance'] = maneuver['distance']
            data['startPoint'] = maneuver['startPoint']
            resp['directions'].append(data)

    return json.dumps(resp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0')
