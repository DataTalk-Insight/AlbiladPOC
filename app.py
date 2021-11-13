import re
import json
import random
import shutil
import tempfile
import os
import logging
import warnings
import shutil

import pandas as pd
import numpy as np
import folium
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe
from sklearn.cluster import KMeans
import matplotlib.cm as cm
import dash_html_components as html
import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import matplotlib.colors as colors
from folium.plugins import HeatMap
from geopy.geocoders import GoogleV3

from utils.process import spoton, location_finder

#spoton(lat, lng, rad, dictionary, data)


MAP_NAME = 'saudi_arabia_map.html'
DEFAULT_MAP_DIR = os.path.join('data', MAP_NAME)

dictionary = pd.read_csv("./data/dictionary.csv")
data = pd.read_csv("./data/place_id_averaged_data.csv")

def get_map(lat, lon, radius):
    #geolocator = GoogleV3(api_key=key)
    #locations = geolocator.reverse(f"{lat}, {lon}")
    #label =locations[0]
    radius = radius * 1000
    map_ = folium.Map(location=[lat, lon], zoom_start=20)
    folium.Marker([lat, lon]).add_to(map_)
    folium.Circle([lat, lon],
                    radius=radius
                   ).add_to(map_)
    folium.Marker(location=[lat,lon],popup=f''' [lat:{lat}, lon:{lon}]
                                                radius: {radius}
                                                
                                             ''',
                  tooltip=f'''<strong>[lat:{lat}, lon:{lon}]</strong>''',
                  icon=folium.Icon(color='red',icon='none')).add_to(map_)
    return map_ #, label

app = dash.Dash(__name__)
server = app.server

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = html.Div([html.Img(
                    src = app.get_asset_url('spoton.png'), 
                     style={
                         'height':'30%', 
                         'width':'20%', 
                         'margin-left': '43%',
                         "margin-top": '3%'}),
                html.H1('Map'),
                html.Iframe(
                            id='map', 
                            srcDoc=open(DEFAULT_MAP_DIR , 'r').read(), 
                            width='100%', 
                            height='600' ),
                html.Br(),
                dcc.Input(id='lat-state', placeholder="latitude", type="number"),
                dcc.Input(id='lon-state', placeholder="longitude", type="number"),
                dcc.Input(id='radius-state', placeholder="radius", type="number"),
                html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
                html.A(html.Button(
                    'Refresh Data'),href='/'),
            
                 html.Div([
                    dcc.Markdown("""
                        **Location and Score**s
                    """),
                    html.Pre(id='selected-data-to-display', style=styles['pre']),
                ], className='three columns'),
                html.Div(id='path-intermediate-value', style={'display': 'none'}),
                html.Div(id='intermediate-value', style={'display': 'none'}),
                html.Div(id='dict-intermediate-value', style={'display': 'none'})
               
                ])
                
@app.callback(
    [
        Output('map', 'srcDoc'),
        Output('path-intermediate-value', 'children'),
        Output('selected-data-to-display', 'children')
    ],
    [
        Input("submit-button-state", "n_clicks"),
    ],
    [
        State("lat-state", "value"),
        State("lon-state", "value"),
        State("radius-state", "value")
    ]
)
def display_selected_data(n_clicks, lat, lon, radius):
    if lat==None or lon==None or radius==None:
        map_dir = None
        marker_dict = None
        return [open(DEFAULT_MAP_DIR , 'r').read(), map_dir, marker_dict] 
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        value_albilad, value_other_banks, albilad_perc_avg_diff, located = spoton(lat, lon, radius, dictionary, data)
    logging.info(f"getting map") 

    map_ = get_map(lat, lon, radius) #, label
    dirpath = tempfile.mkdtemp()
    map_dir = os.path.join(dirpath, MAP_NAME)
    logging.info(f"saving map") 
  
    map_.save(map_dir)
    marker_dict = {}
  
    if located is True:
        #marker_dict['Address'] = label
        marker_dict['lat/lon'] = [lat,lon]
        marker_dict['Radius'] = radius
        marker_dict[f'Al-Bilad banks/atm present in location'] = True
        marker_dict[f'Average foot traffic of Al-Bilad bank per hour is'] = value_albilad
        
    elif located is False:
        #marker_dict['Address'] = label
        marker_dict['lat/lon'] = [lat, lon]
        marker_dict['Radius'] = radius
        marker_dict[f'Al-Bilad banks/atm present in location'] = False
        marker_dict[f'If opened, Average foot traffic of Al-Bilad bank per hour will be'] = value_albilad
    else:
      
        dirpath = tempfile.mkdtemp()
        try:
            shutil.copy(DEFAULT_MAP_DIR, dirpath)
            logging.info("File copied successfully.")
        except shutil.SameFileError:
            logging.info("Source and destination represents the same file.")
        # If destination is a directory.
        except IsADirectoryError:
            logging.info("Destination is a directory.")
        # If there is any permission issue
        except PermissionError:
            logging.info("Permission denied.")
        # For other errors
        except:
            logging.info("Error occurred while copying file.")
        map_dir = os.path.join(dirpath, MAP_NAME)
        marker_dict['message'] = "No Bank/ATM in this area, try using different coordinates or increasing the radius"

    marker_dict = json.dumps(marker_dict , indent = 4)  
    return [open(map_dir, 'r').read(), map_dir, marker_dict]

@app.callback(
    Output('intermediate-value', 'children'),
    Input('path-intermediate-value', 'children'),
    )
def delete_tmpdir(path):
    if path:
        path, file_name= os.path.split(path)
        shutil.rmtree(path)
        logging.info(f"directory {path} removed") 
        return "directory removed"
    return "no directory to remove"

if __name__ == "__main__":
    app.run_server(debug=True)

