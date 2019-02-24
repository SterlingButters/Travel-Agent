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


import forecastiopy as cast

Lisbon = [38.7252993, -9.1500364]

fio = cast.ForecastIO.ForecastIO('163bc202ba47de2514c47f63f1872dd7', latitude=Lisbon[0], longitude=Lisbon[1])
current = cast.FIOCurrently.FIOCurrently(fio)

print(current.currently) # 'apparentTemperature', 'cloudCover', 'currently', 'dewPoint', 'get', 'humidity', 'icon', 'ozone', 'precipIntensity', 'precipProbability', 'pressure', 'summary', 'temperature', 'time', 'uvIndex', 'visibility', 'windBearing', 'windGust', 'windSpeed']
print('Temperature:', current.temperature)
print('Precipitation Probability:', current.precipProbability)


# scl = [0,"rgb(150,0,90)"],        [0.125,"rgb(0, 0, 200)"],   [0.25,"rgb(0, 25, 255)"],\
#       [0.375,"rgb(0, 152, 255)"], [0.5,"rgb(44, 255, 150)"],  [0.625,"rgb(151, 255, 0)"],\
#       [0.75,"rgb(255, 234, 0)"],  [0.875,"rgb(255, 111, 0)"], [1,"rgb(255, 0, 0)"]
#
#
# weather_plot = go.Scattermapbox(
#         lat=[],
#         lon=[],
#         name='Precipitation',
#         mode='markers',
#         # text=,
#         # hoverinfo='text',
#         marker=dict(size=2),
#     )
#
# data = [weather_plot]
#
# layout = go.Layout(
#     height=750,
#     width=1250,
#     hovermode='closest',
#     mapbox=dict(
#         accesstoken=mapbox_access_token,
#         style='streets',
#         center=center,
#         bearing=bearing,
#         pitch=pitch,
#         zoom=zoom
#     ),
#     colorscale=scl
# )
#
# fig = { 'data':data, 'layout':layout }
# py.iplot(fig, filename='precipitation')
