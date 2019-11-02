from flask import Flask
import requests
import json

key = 'D2ZCny0cmDMUDUbsavWda8qvTD9K3iRV'
app = Flask(__name__)

@app.route('/')
def get_directions():
    params = {'key': key, 'from': '1900 Summit Street Columbus Ohio', 'to': '1494 North High Street Columbus Ohio', 'routeType': 'pedestrian', 'narrativeType': 'html'}
    content = requests.get('http://www.mapquestapi.com/directions/v2/route', params=params).content
    parsed_json = json.loads(content)
    return content


if __name__ == '__main__':
   app.run(debug=True)