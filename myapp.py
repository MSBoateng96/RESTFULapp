from flask import Flask, render_template, request, jsonify
from cassandra.cluster import Cluster
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
import json
import requests
import  requests_cache

requests_cache.install_cache('crime_api_cache', backend='sqlite', expire_after=36000)

cluster = Cluster(['cassandra'])
session = cluster.connect()
app = Flask(__name__)

stops_url_template = 'https://data.police.uk/api/stops-street?lat={lat}&lng={lng}&date={data}'

@app.route('/', methods=['GET'])
def home():
        return 'Welcome to my restful app'

@app.route('/stopandsearch',  methods=['GET', 'POST'])
def stopschart():
    my_latitude = request.args.get('lat','52.629729')
    my_longitude = request.args.get('lng','-1.131592')
    my_date = request.args.get('date','2018-06')

    stops_url = stops_url_template.format(lat = my_latitude, lng = my_longitude, data = my_date)

    resp = requests.get(stops_url)
    if resp.ok:
        stops = resp.json()
    else:
        print(resp.reason)

    search_outcome_stats = {'None': 0}
    for stop in stops:
        outcome = stop["outcome"]
        if not outcome:
            search_outcome_stats['None'] += 1
        elif outcome not in search_outcome_stats.keys():
            search_outcome_stats.update({outcome:1})
        else:
            search_outcome_stats[outcome] += 1

    search_object_stats = {'None': 0}
    for stop in stops:
        object_of_search = stop["object_of_search"]
        if not object_of_search:
            search_object_stats['None'] += 1
        elif object_of_search not in search_object_stats.keys():
            search_object_stats.update({object_of_search:1})
        else:
            search_object_stats[object_of_search] += 1

    search_ethnicity_stats = {'None': 0}
    for stop in stops:
        ethnicity = stop["self_defined_ethnicity"]
        if not ethnicity:
            search_ethnicity_stats['None'] += 1
        elif ethnicity not in search_ethnicity_stats.keys():
            search_ethnicity_stats.update({ethnicity:1})
        else:
            search_ethnicity_stats[ethnicity] += 1

    graphs = [
            dict(
                data=[
                    dict(
                        values=list(search_ethnicity_stats.values()),
                        labels=list(search_ethnicity_stats.keys()),
                        hole=.4,
                        type='pie',
                        name='Ethnicity'
                    ),
                ],
                layout=dict(
                    title='Stop & Search By Ethnicity Stats During {}'.format(my_date)
                )
            ),
            dict(
                data=[
                    dict(
                        values=list(search_object_stats.values()),
                        labels=list(search_object_stats.keys()),
                        hole=.4,
                        type='pie',
                        name='Object'
                    ),
                ],
                layout=dict(
                    title='Object of Search Stats During {}'.format(my_date)
                )
            ),
            dict(
                data=[
                    dict(
                        values=list(search_outcome_stats.values()),
                        labels=list(search_outcome_stats.keys()),
                        hole=.4,
                        type='pie',
                        name='Outcome'
                    ),
                ],
                layout=dict(
                    title='Outcome of Search Stats During {}'.format(my_date)
                )
            ),
        ]

    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    graphJSON = json.dumps(graphs, cls=PlotlyJSONEncoder)
    return render_template('plotholder.html',ids=ids,graphJSON=graphJSON)

if __name__=="__main__":
    app.run(host='0.0.0.0', port=8080)
