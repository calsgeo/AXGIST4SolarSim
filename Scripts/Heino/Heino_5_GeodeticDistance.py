import math
import pyproj
import geopy.distance
import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt
import os
from datetime import datetime
import geopandas as gpd
import shapely
import rasterio
import glob

print("Script starts")
type = "full" # test, test_Europe, full simulation

script_folder = os.path.abspath(__file__)
data_folder = os.path.dirname(os.path.dirname(os.path.dirname(script_folder)))
data_subfolder = 'Input_Data'
location = 'Heino'
csv_input = 'csv'
raster_input = 'outputRaster'
vector_input = 'Vector'
root_folder = os.path.join(data_folder,data_subfolder,location)

high_res_region = 2000

os.chdir(root_folder)
print(root_folder)

def distance(x_o, y_o, x_s, y_s):
    d = math.dist([x_o, y_o], [x_s, y_s])
    return d

def angle_value(a,b):
    if a==0:
        c = 0
    else:
        c = math.degrees(math.atan2(a,b))
    return c

def get_bearing(lat1, long1, lat2, long2):
    dLon = (long2 - long1)
    x = math.cos(math.radians(lat2)) * math.sin(math.radians(dLon))
    y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(dLon))
    brng = np.arctan2(x,y)
    brng = np.degrees(brng)
    if brng < 0:
        brng = 360+brng
    else:
        pass
    return brng

def time_delta(time_start,message):
    time_finish = datetime.now()
    # get difference
    delta = time_finish - time_start
    sec = delta.total_seconds()
    (hours, sec) = divmod(sec, 3600)
    (minutes, sec) = divmod(sec, 60)
    formatted = f"{hours:02.0f}:{minutes:02.0f}:{sec:05.2f}"
    print(f'Time in {message}:', formatted)

def zenith_view(df):
    df['dif_z'] = df['Z'].values - df['h_wsta'].values
    df["elevation_pyproj"] = list(map(angle_value, df['dif_z'],df['distance_pyproj']))
    df['zenith_view_pyproj'] = 90- df['elevation_pyproj'].values
    return df

def azimuth_adjustment(df,base):
    # Turns the negative azimuth values to positive and calculates the classes for the further classification
    df[f'{base}_360'] =  np.where(df[f'{base}'] < 0, 360 + df[f'{base}'], df[f'{base}'])
    df[f'{base}_class360'] =  np.where(df[f'{base}_360'] > 359.5, 0, round(df[f'{base}_360'],0))
    return df

def geom_filter(poly_geom,point_geom):
    test_filter = poly_geom.contains(point_geom)
    return test_filter

start_time = datetime.now()
current_time = start_time
print(f"-----    Start time: {start_time}")

input_folder = os.path.join(root_folder,csv_input)

weatherStation = os.path.join(root_folder,vector_input,"INSPIRE_weatherLocation_28992.gml")

# Read shape file (created by Las Bound) using geopandas
ws_location = gpd.read_file(weatherStation,driver='GML')
ws_location = ws_location.explode(index_parts=False)
coords = [(x,y) for x, y in zip(ws_location.geometry.x, ws_location.geometry.y)]
ws_location_w84 = ws_location.to_crs(epsg=4326)
east_wsLocation = ws_location.geometry.x[0]
north_wsLocation = ws_location.geometry.y[0]
lon_wsLocation = ws_location_w84.geometry.x[0]
lat_wsLocation = ws_location_w84.geometry.y[0]
print(f"{lat_wsLocation},{lon_wsLocation}")

src = rasterio.open(os.path.join(root_folder,raster_input,"AHN_05m_dsm_1200m_InputDEM.tif"))
epsg_code = int(src.crs.data['init'][5:])
for val in src.sample(coords):
    ws_height = round(val[0] + 1.5,2)

print(f'Weather station coordinates: {lat_wsLocation} - {lon_wsLocation} - {ws_height}')
g = pyproj.Geod(ellps='WGS84') # for the azimuth calculation

list_csv = glob.glob(os.path.join(input_folder,'*.csv'))

listHR_csv = ['AHN_05m_dsm_1200m_InputDEM_Points','AHN_1m_dsm_1200m_InputDEM_Points']

for input_csv in list_csv:
    input_csv = input_csv.split('/')[-1]
    input_csv = input_csv.split('.')[0]

    csv_time = datetime.now()
    csv_time = current_time
    print(f"Start time for csv {input_csv}: {csv_time}")
    
    if "AHN3_05m" in input_csv:
        dist_base = 1200
    elif "AHN3_1m" in input_csv:
        dist_base = 1200
    elif input_csv == "AHN4_05m_dsm_Heino":
        dist_base = 2500
    elif input_csv == "AHN3_5m_dsm":
        dist_base = 20000
    else:
        dist_base = 100000

    if type == "test":
        csv_file = os.path.join(input_folder, f"test_dataset.csv") # Test dataset
        separator = ","
    elif type == "test_Europe":
        csv_file = os.path.join(input_folder, f"Test_DEM_Europe.csv") # Test dataset
        separator = ","
    else:
        csv_file = os.path.join(input_folder, f"{input_csv}.csv")
        separator = ","

    ################ reads the csv file
    df_csv = pd.read_csv(csv_file, sep=separator)
    time_delta(current_time,"Read csv file")
    current_time = datetime.now()

    print(f"Dataframe shape before spatial filtering: {df_csv.shape}")

    df_csv = df_csv.pipe(gpd.GeoDataFrame, geometry=gpd.points_from_xy(df_csv.X, df_csv.Y, df_csv.Z), crs=f'epsg:{epsg_code}')
    time_delta(current_time,"GeoDataFrame creation")
    current_time = datetime.now()

    # Creates a spatial filter to not process points inside the high csv area of interest
    if input_csv not in listHR_csv:
        env_ws_location = ws_location.buffer(high_res_region).envelope
        envgdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries(env_ws_location))
        envgdf['times'] = len(df_csv)
        envgdf = envgdf.loc[envgdf.index.repeat(envgdf.times)].reset_index(drop=True)
        df_csv["within"] = list(map(geom_filter,envgdf["geometry"],df_csv["geometry"] ))
        time_delta(current_time,"Spatial Filter")
        current_time = datetime.now()
        df_csv = df_csv[df_csv["within"]==False]
        print(f"Dataframe shape after spatial filtering: {df_csv.shape}")

    df_csv = df_csv.to_crs(epsg=4326)
    df_csv['lon'] = df_csv.geometry.x
    df_csv['lat'] = df_csv.geometry.y

    df_csv['lon_wsta'] = lon_wsLocation
    df_csv['lat_wsta'] = lat_wsLocation
    df_csv['h_wsta'] = ws_height

    df_csv['north_wsta'] = north_wsLocation
    df_csv['east_wsta'] = east_wsLocation

    df_csv['geom_wsta'] = gpd.points_from_xy(df_csv.lon_wsta, df_csv.lat_wsta, df_csv.h_wsta)

    df_csv = df_csv.reset_index(drop=True)

    time_delta(current_time,"Adds Weather station point location")
    current_time = datetime.now()
    

    df_cal = df_csv.join(pd.DataFrame([g.inv(p1.x, p1.y, p2.x, p2.y) if p1 and p2 else (None, None, None) for p1, p2 in zip(df_csv.geom_wsta, df_csv.geometry) ], columns=['azimuth_pyproj', 'azimuth_back_pyproj', 'distance_pyproj'] ) )
    time_delta(current_time,"Geodetic calculation")
    current_time = datetime.now()
    del df_csv
    df_cal = zenith_view(df_cal)
    time_delta(current_time,"execution of Zenith function")
    current_time = datetime.now()
    df_cal = azimuth_adjustment(df_cal,'azimuth_pyproj')
    time_delta(current_time,"execution of Azimuth function")
    current_time = datetime.now()

    # Numpy distance calculation
    df_cal["euclidean_distance"] = list(map(distance, df_cal['X'],df_cal['Y'], df_cal['east_wsta'],df_cal['north_wsta']))

    # Bearing calculation,elevation,zenith
    df_cal["azimuth_bearing"] = list(map(get_bearing, df_cal['lat_wsta'],df_cal['lon_wsta'], df_cal['lat'],df_cal['lon']))
    df_cal = azimuth_adjustment(df_cal,'azimuth_bearing')
    df_cal["elevation_manual"] = list(map(angle_value, df_cal['dif_z'],df_cal['euclidean_distance']))
    df_cal["zenith_view_manual"] =90-df_cal["elevation_manual"].values
    time_delta(current_time,"Manual features calculation")

    df_cal["distance_comparison"] = abs(df_cal['distance_pyproj'].values - df_cal['euclidean_distance'].values)
    df_cal["azimuth_comparison"] = abs(df_cal['azimuth_pyproj'].values - df_cal['azimuth_bearing'].values)
    df_cal["elevation_comparison"] = abs(df_cal['elevation_pyproj'].values - df_cal['elevation_manual'].values)
    df_cal["azimuth_class_comparison"] = abs(df_cal['azimuth_pyproj_class360'].values - df_cal['azimuth_bearing_class360'].values)
    current_time = datetime.now()
    time_delta(current_time,"Features comparison")

    df_cal.drop(['geometry','geom_wsta'], axis=1, inplace=True)
    current_time = datetime.now()
    time_delta(current_time,"Drop attributes")
    df_cal.to_csv(os.path.join(input_folder,f'{input_csv}_Calc.csv'),index=False)
    time_delta(current_time,"Dataframe writing")
    current_time = datetime.now()
    time_delta(csv_time,f"End Time: {current_time} - Total Time")
current_time = datetime.now()
time_delta(start_time,f"Total Time: {current_time}")