from flask import Flask, render_template
import requests
import json

key = 'D2ZCny0cmDMUDUbsavWda8qvTD9K3iRV'
app = Flask(__name__)

@app.route('/directions')
def get_directions():
    params = {'key': key, 'from': '1900 Summit Street Columbus Ohio', 'to': '1494 North High Street Columbus Ohio', 'routeType': 'pedestrian', 'narrativeType': 'html'}
    content = requests.get('http://www.mapquestapi.com/directions/v2/route', params=params).content
    parsed_json = json.loads(content)
    return content

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
   app.run(host = '0.0.0.0', debug=True)