import plotly.plotly as py
import plotly.graph_objs as go
import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Output, State, Input
import googlemaps
import polyline
import numpy as np
import math
import json


from forecastiopy import *
from datetime import datetime
import tzlocal

gmaps = googlemaps.Client(key=google_maps_api_key)


# TODO Write as Class
def get_route(address_start='Houston, TX', address_end='Austin, TX'):
    if address_start and address_end:

        address_start = gmaps.geocode(address_start)[0]['geometry']['location']
        address_end = gmaps.geocode(address_end)[0]['geometry']['location']

        start = (address_start['lat'], address_start['lng'])
        end = (address_end['lat'], address_end['lng'])

        directions = gmaps.directions(start, end)

        path = []
        waypoints = []
        instructions = []
        path.append(start)  # add starting coordinate to trip
        waypoints.append(start)
        for index in range(len(directions[0]['legs'][0]['steps'])):
            instruction = directions[0]['legs'][0]['steps'][index]['html_instructions']
            instructions.append(instruction)

            start_coords = directions[0]['legs'][0]['steps'][index]['start_location']
            path.append((start_coords['lat'], start_coords['lng']))
            waypoints.append((start_coords['lat'], start_coords['lng']))

            poly_coords = directions[0]['legs'][0]['steps'][index]['polyline']['points']
            path.extend(polyline.decode(poly_coords))

            if index == len(directions[0]['legs'][0]['steps']) - 1:
                instruction = directions[0]['legs'][0]['steps'][index]['html_instructions']
                instructions.append(instruction)

                end_coords = directions[0]['legs'][0]['steps'][index]['end_location']
                path.append((end_coords['lat'], end_coords['lng']))
                waypoints.append((end_coords['lat'], end_coords['lng']))

        path.append(end)  # add ending coordinate to trip
        waypoints.append(end)

        return path, waypoints, instructions

# HOUSTON = [29.760427, -95.369804]

# print(json.dumps(currently.currently, indent=2, sort_keys=True))
# print(json.dumps(minutely.minutely, indent=2, sort_keys=True))
# print(json.dumps(hourly.hourly, indent=2, sort_keys=True))
# print(json.dumps(daily.daily, indent=2, sort_keys=True))
# print(json.dumps(alerts.alerts, indent=2, sort_keys=True))


local_timezone = tzlocal.get_localzone()

path, waypoints, instructions = get_route()

new_lats = []
new_longs = []
probs = []

# https://gis.stackexchange.com/questions/142326/calculating-longitude-length-in-miles

print(len(path))

for i in range(0, len(path), 10):
    print(i)
    new_lats.append(path[i][0])
    new_longs.append(path[i][1])
    client = ForecastIO.ForecastIO(darksky_api_key, latitude=path[i][0], longitude=path[i][1],
                                   units='us')

    if client.has_hourly() is True:
        hourly = FIOHourly.FIOHourly(client)
        probs.append(float(hourly.get_hour(1)['precipProbability']))

    # if client.has_minutely() is True:
    #     minutely = FIOMinutely.FIOMinutely(client)
    #     print('Minutely')
    #     print('Summary:', minutely.summary)
    #
    #     for minute in range(0, minutely.minutes()):
    #         print('Minute', minute)
    #         for item in ['time', 'precipIntensity', 'precipProbability']:
    #             if item == 'time':
    #                 print(datetime.fromtimestamp(float(minutely.get_minute(minute)[item]), local_timezone))
    #             else:
    #                 print(str(minutely.get_minute(minute)[item]))
    #
    #         # Print all keys
    #         # for item in minutely.get_minute(minute).keys():
    #         #     print(item + ' : ' + str(minutely.get_minute(minute)[item]))
    # else:
    #     print('No Minutely data')
    #
    # if client.has_hourly() is True:
    #     hourly = FIOHourly.FIOHourly(client)
    #     print('Hourly')
    #     print('Summary:', hourly.summary)
    #
    #     for hour in range(0, hourly.hours()):
    #         print('Hour', hour)
    #         for item in ['time', 'precipIntensity', 'precipProbability', 'cloudCover', 'visibility']:
    #             if item == 'time':
    #                 print(datetime.fromtimestamp(float(minutely.get_minute(minute)[item]), local_timezone))
    #             else:
    #                 print(str(hourly.get_hour(hour)[item]))
    #
    #         # Print all keys
    #         # for item in hourly.get_hour(hour).keys():
    #         #     print(item + ' : ' + str(hourly.get_hour(hour)[item]))
    # else:
    #     print('No Hourly data')
    #
    # if client.has_daily() is True:
    #     daily = FIODaily.FIODaily(client)
    #     print('Daily')
    #     print('Summary:', daily.summary)
    #
    #     for day in range(0, daily.days()):
    #         print('Day', day)
    #         for item in ['time', 'precipIntensity', 'precipProbability', 'cloudCover', 'visibility']:
    #             if item == 'time':
    #                 print(datetime.fromtimestamp(float(minutely.get_minute(minute)[item]), local_timezone))
    #             else:
    #                 print(str(daily.get_day(day)[item]))
    #
    #         # Print all keys
    #         # for item in daily.get_day(day).keys():
    #         #     print(item + ' : ' + str(daily.get_day(day)[item]))
    # else:
    #     print('No Daily data')


scl = [0, "rgb(150,0,90)"],        [0.125,"rgb(0, 0, 200)"],   [0.25,"rgb(0, 25, 255)"],\
      [0.375,"rgb(0, 152, 255)"], [0.5,"rgb(44, 255, 150)"],  [0.625,"rgb(151, 255, 0)"],\
      [0.75,"rgb(255, 234, 0)"],  [0.875,"rgb(255, 111, 0)"], [1,"rgb(255, 0, 0)"]


weather_plot = go.Scattermapbox(
        lat=new_lats,
        lon=new_longs,
        name='Precipitation',
        mode='markers',
        text=probs,
        hoverinfo='all',
        marker=dict(
            color=probs,
            colorscale=scl,
            reversescale=True,
            opacity=0.7,
            size=5
        ),
    )

data = [weather_plot]

layout = go.Layout(
    height=750,
    width=1250,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style='streets',
        # center=center,
        # bearing=bearing,
        # pitch=pitch,
        # zoom=zoom
    ),
)

fig = go.Figure(data=data, layout=layout)
py.iplot(fig, filename='precipitation', auto_open=True)


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#
# app = dash.Dash(external_stylesheets=external_stylesheets)
# app.config['suppress_callback_exceptions'] = True
#
# app.layout = html.Div([
#     dcc.Graph(id='map')
# ])
# if __name__ == '__main__':
#     app.run_server(debug=True)
