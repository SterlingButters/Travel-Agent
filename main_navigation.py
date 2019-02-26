# https://console.cloud.google.com/google/maps-apis/api-list?project=travelagent-1550711664727&consoleReturnUrl=https:%2F%2Fcloud.google.com%2Fmaps-platform%2F%3Fapis%3Dmaps,routes,places%26project%3Dtravelagent-1550711664727&consoleUI=CLOUD
# https://studio.mapbox.com/styles/sterlingbutters/cjscjbxk00coa1fpao22j7j5o/edit/
# https://stackoverflow.com/questions/40877840/google-maps-api-draw-a-route-using-points-of-a-polyline
# 9MUU

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
from geographiclib.geodesic import Geodesic

gmaps = googlemaps.Client(key=google_maps_api_key)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True

#######################################################################################################################

app.layout = html.Div([
    html.H2('Travel Agent Application'),

    html.Div([
        html.Div([dcc.Input(id='from-location', placeholder='Starting Location', size=50, style=dict(height=30),
                            value='me')],
                 style=dict(
                     width='0%',
                     display='table-cell',
                     verticalAlign="middle",
                 )
                 ),
        html.Div([daq.ToggleSwitch(id='switch-fields', label='Switch To/From', labelPosition='bottom')],
                 style=dict(
                     width='50%',
                     display='table-cell',
                     verticalAlign="bottom",
                 )
                 ),
        html.Div([dcc.Input(id='to-location', placeholder='Destination', size=50, style=dict(height=30),
                            value='Houston, TX')],
                 style=dict(
                     width='0%',
                     display='table-cell',
                     verticalAlign="middle",
                 )
                 ),
    ],
        style=dict(
            width='100%',
            display='table',
        ),
    ),

    html.Button('Plot Directions', id='start-nav'),

    html.Button('Add Route', id='add-route'),
    html.Br(),

    dcc.Store(id='stored-directions', storage_type='session'),

    html.Div([
        html.Div([daq.Slider(
            id='pitch',
            vertical=True,
            min=0,
            max=100,
            value=20,
            handleLabel={"showCurrentValue": True, "label": "Pitch"},
        )],
            style=dict(
                width='100%',
                display='table-cell',
                verticalAlign="middle",
            )
        ),
        html.Div([daq.Knob(
            id='bearing',
            label="Bearing",
            value=0,
            min=-180,
            max=180,
            scale={'start': -180, 'labelInterval': 60, 'interval': 1}
        )],
            style=dict(
                width='0%',
                display='table-cell',
                verticalAlign="bottom",
            )
        ),
        html.Div([daq.Slider(
            id='zoom',
            vertical=True,
            min=0,
            max=20,
            value=5,
            handleLabel={"showCurrentValue": True, "label": "Zoom"},
        )],
            style=dict(
                width='0%',
                display='table-cell',
                verticalAlign="middle",
            )
        ),
    ],
        style=dict(
            width='100%',
            display='table',
        ),
    ),

    dcc.Graph(id='map'),

    html.Div([
        html.P('Trip Progress:'),
        dcc.Slider(id='current-location', updatemode='drag', value=0, included=True, min=0, max=1000,
                   marks={
                       0: {'label': 'Journey Start', 'style': {'color': '#77b0b1'}},
                       1000: {'label': 'Journey End', 'style': {'color': '#77b0b1'}},
                   }),
        daq.BooleanSwitch(id='active-view', on=False, label='Reorient')
    ]),
])


#######################################################################################################################


def get_route(address_start, address_end):
    if address_start and address_end:

        address_start = gmaps.geocode(address_start)[0]['geometry']['location']
        address_end = gmaps.geocode(address_end)[0]['geometry']['location']

        start = (address_start['lat'], address_start['lng'])
        end = (address_end['lat'], address_end['lng'])

        directions = gmaps.directions(start, end)

        # print(json.dumps(directions[0],
        #                  indent=2,
        #                  sort_keys=True))

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


def get_bearing(lat1, lat2, long1, long2):
    brng = Geodesic.WGS84.Inverse(lat1, long1, lat2, long2)['azi1']
    return brng


def create_gridpoints(lat1, lat2, long1, long2, n=25, m=25):
    brng = Geodesic.WGS84.Inverse(lat1, long1, lat2, long2)['azi1']
    Tdist = Geodesic.WGS84.Inverse(lat1, long1, lat2, long2)['s12']

    dist = Tdist/n

    # Get list of m evenly spaced lat/lon pairs "above" and "below" origin-destination straight-line
    upper = brng + 90
    lower = brng - 90
    u_origin_base = []
    l_origin_base = []

    lat_u = lat_l = lat1
    lon_u = lon_l = long1
    for i in range(m):
        u_origin_base.append((lat_u, lon_u))
        lat_u = Geodesic.WGS84.Direct(lat_u, lon_u, upper, dist)['lat2']
        lon_u = Geodesic.WGS84.Direct(lat_u, lon_u, upper, dist)['lon2']

        l_origin_base.append((lat_l, lon_l))
        lat_l = Geodesic.WGS84.Direct(lat_l, lon_l, lower, dist)['lat2']
        lon_l = Geodesic.WGS84.Direct(lat_l, lon_l, lower, dist)['lon2']

    origin_base = []
    origin_base.extend(l_origin_base[::-1])
    origin_base.extend(u_origin_base)

    # Get list of n evenly spaced lat/lon pairs between origin and destination
    length_base = []
    for k in range(len(origin_base)):
        lat = origin_base[k][0]
        lon = origin_base[k][1]
        for j in range(n):
            lat = Geodesic.WGS84.Direct(lat, lon, brng, dist)['lat2']
            lon = Geodesic.WGS84.Direct(lat, lon, brng, dist)['lon2']
            length_base.append((lat, lon))

    print(len(length_base))
    print(length_base)

    return length_base

#######################################################################################################################


@app.callback(
    Output('from-location', 'value'),
    [Input('switch-fields', 'value')],
    [State('from-location', 'value'),
     State('to-location', 'value')]
)
def switch_field(switch, from_location, to_location):
    if not switch:
        # print("start to field 1")
        return from_location
    else:
        # print("destination to field 1")
        return to_location


@app.callback(
    Output('to-location', 'value'),
    [Input('switch-fields', 'value')],
    [State('from-location', 'value'),
     State('to-location', 'value')]
)
def switch_field(switch, from_location, to_location):
    if switch:
        # print("start to field 2")
        return from_location
    else:
        # print("destination to field 2")
        return to_location


###########################################

# Define value of bearing knob
@app.callback(
    Output('bearing', 'value'),
    [Input('stored-directions', 'modified_timestamp'),
     Input('active-view', 'on'),
     Input('current-location', 'value')],
    [State('bearing', 'value'),
     State('stored-directions', 'data')]
)
def define_bearing(ts, pov_view, location, bearing_state, data):
    if ts is None:
        raise PreventUpdate

    path = data['path'] if data else []

    if pov_view:
        lat1 = path[int(len(path) * location / 1000)][0]
        lat2 = path[int(len(path) * location / 1000) + 1][0]
        lng1 = path[int(len(path) * location / 1000)][1]
        lng2 = path[int(len(path) * location / 1000) + 1][1]
        bearing = get_bearing(lat1, lat2, lng1, lng2)
        return bearing

    else:
        return bearing_state


# TODO: Doesnt Disable Slider
# @app.callback(
#     Output('bearing', 'disabled'),
#     [Input('active-view', 'on')],
# )
# def define_bearing(pov_view):
#     if pov_view:
#         print('on')
#         return False
#     else:
#         return True


# Define value of Pitch Slider
@app.callback(
    Output('pitch', 'value'),
    [Input('active-view', 'on')],
    [State('pitch', 'value')]
)
def define_pitch(pov_view, pitch_state):
    if pov_view:
        return 20
    else:
        return pitch_state


# Define Value of Zoom Slider
@app.callback(
    Output('zoom', 'value'),
    [Input('active-view', 'on')],
    [State('zoom', 'value')]
)
def define_zoom(pov_view, zoom_state):
    if pov_view:
        return 15
    else:
        return zoom_state


# Store values to memory
@app.callback(Output('stored-directions', 'data'),
              [Input('start-nav', 'n_clicks')],
              [State('from-location', 'value'),
               State('to-location', 'value'),
               State('stored-directions', 'data')])
def store_directions(click, address_start, address_end, data):
    if click:
        # Give a default data dict with empty lists if there's no data.
        data = data or {'path': [], 'waypoints': [], 'instructions': [], 'weather': []}

        data['path'], data['waypoints'], data['instructions'] = get_route(address_start, address_end)

        return data


# Output data stores into figure
@app.callback(Output('map', 'figure'),
              [Input('stored-directions', 'modified_timestamp'),
               Input('active-view', 'on'),
               Input('current-location', 'value'),
               Input('bearing', 'value'),
               Input('pitch', 'value'),
               Input('zoom', 'value')],
              [State('stored-directions', 'data')])
def on_data(ts, pov_view, location, bearing, pitch, zoom, data):
    if ts is None:
        raise PreventUpdate

    path = data['path'] if data else []
    waypoints = data['waypoints'] if data else []
    instructions = data['instructions'] if data else []

    weatherpts = create_gridpoints(lat1=path[0][0], lat2=path[-1][0], long1=path[0][1], long2=path[-1][1]) if data else []

    path_plot = go.Scattermapbox(
        lat=[item_x[0] for item_x in path],
        lon=[item_y[1] for item_y in path],
        name='Path',
        mode='lines',
        # line=dict(shape='spline') # not supported for mapbox
    )

    waypoint_plot = go.Scattermapbox(
        lat=[item_x[0] for item_x in waypoints],
        lon=[item_y[1] for item_y in waypoints],
        name='Instructions',
        mode='markers',
        text=instructions,
        hoverinfo='text',
        marker=dict(size=[8] + [5 for j in range(len(waypoints) - 2)] + [8]),
    )

    weather_plot = go.Scattermapbox(
        lat=[item_x[0] for item_x in weatherpts],
        lon=[item_y[1] for item_y in weatherpts],
        name='Weather',
        mode='markers',
        text='',
        hoverinfo='all',
        marker=dict(size=3),
    )

    if location:
        location_plot = go.Scattermapbox(
            lat=[path[int(len(path) * location / 1000)][0]],
            lon=[path[int(len(path) * location / 1000)][1]],
            name='My Location',
            mode='markers',
            marker=dict(size=12,
                        # symbol='car',
                        # symbol='triangle-stroked', # https://labs.mapbox.com/maki-icons/
                        # color='green'
                        ),
        )

        data = [path_plot, waypoint_plot, weather_plot, location_plot]

    else:
        data = [path_plot, waypoint_plot, weather_plot]

    if not pov_view and not location:
        center = dict(lat=np.mean([float(step[0]) for step in path]),
                      lon=np.mean([float(step[1]) for step in path]))
    else:
        center = dict(lat=path[int(len(path) * location / 1000)][0],
                      lon=path[int(len(path) * location / 1000)][1])

    layout = go.Layout(
        height=750,
        width=1250,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            style='streets',
            center=center,
            bearing=bearing,
            pitch=pitch,
            zoom=zoom
        ),
    )

    fig = dict(data=data, layout=layout)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
