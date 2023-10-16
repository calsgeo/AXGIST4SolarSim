import math
from pyproj import Geod
import geopy.distance
import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt
import os
from datetime import datetime
import random
import glob

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

list_csv = glob.glob(os.path.join(root_folder,csv_input,'*5m*Calc.csv'))
def time_delta(time_start,message):
    time_finish = datetime.now()
    # get difference
    delta = time_finish - time_start
    sec = delta.total_seconds()
    (hours, sec) = divmod(sec, 3600)
    (minutes, sec) = divmod(sec, 60)
    formatted = f"{hours:02.0f}:{minutes:02.0f}:{sec:05.2f}"
    print(f'Time in {message}:', formatted)

def view_calculation(df):
    var = "elevation_pyproj"
    df_agg = df.groupby(['azimuth_pyproj_class360'], sort=False)[var].max().reset_index()
    df_agg = df_agg.sort_values(by=['azimuth_pyproj_class360'], ascending=True)
    df_agg['azimuth_hor'] = np.where(df_agg['azimuth_pyproj_class360'] != 360, df_agg['azimuth_pyproj_class360']-180, -180)
    df_filtered = pd.merge(df, df_agg, how='inner')
    df_agg_hor = df_agg[['azimuth_hor',var]]
    return df_agg_hor,df_filtered

def check_folder(folder):
    # Create a new directory because it does not exist
    isExist = os.path.exists(folder)
    if not isExist:
        os.makedirs(folder)
        print("The output directory is created!")

for inputcsv in list_csv:
    if 'base_' in inputcsv:
        pass
    else:
        inputcsv = inputcsv.split('/')[-1]
        inputcsv = inputcsv.split('.')[0]
        if "AHN_05m" in inputcsv:
            minDistance = 100
            dist_base = 1200
            interval = 100
        elif "AHN_1m" in inputcsv:
            minDistance = 100
            dist_base = 1200
            interval = 100
        elif "AHN_5m" in inputcsv:
            minDistance = 1500
            dist_base = 20000
            interval = 500
        else:
            minDistance = 1500
            dist_base = 100000
            interval = 1000

        current_time = datetime.now()
        start_time = current_time
        print("    -----    ------   ")
        print(f"Horizon file creation for {inputcsv} Start time: {current_time}")

        csv_file = os.path.join(root_folder,csv_input,f'{inputcsv}.csv')
        
        inputRaster = inputcsv.replace('_Points_Calc','')
        folder_csv = os.path.join(root_folder,csv_input,f"{inputRaster}","csv")
        folder_hor = os.path.join(root_folder,csv_input,f"{inputRaster}","hor")

        check_folder(folder_csv)
        check_folder(folder_hor)

        df_csv = pd.read_csv(csv_file)
        time_delta(current_time,"Read csv file")
        current_time = datetime.now()

        list_distances = list(range(minDistance,dist_base+interval,interval))

        list_distances.sort(reverse=True)
        for d in list_distances:
            df_csv_filtered =df_csv[df_csv.distance_pyproj.values <= d].copy()
            print(f"Filter data at distance {d}")
            df_agg,df_filtered = view_calculation(df_csv_filtered)
            df_agg.to_csv(os.path.join(folder_hor,f'{inputcsv}_ProfileData_Distance_{d}m.hor'),index=False)
            df_filtered.to_csv(os.path.join(folder_csv,f'{inputcsv}_inputData_plot{d}m.csv'),index=False)

        df_agg,df_filtered = view_calculation(df_csv)
        time_delta(current_time,"Full dataset calculation time: ")
        current_time = datetime.now()

        df_agg.to_csv(os.path.join(folder_hor,f'{inputcsv}_ProfileData_Distance_full.hor'),index=False)
        df_filtered.to_csv(os.path.join(folder_csv,f'{inputcsv}_InputData_plot_full.csv'),index=False)

        time_delta(current_time,"Full results storage")
        end_time = datetime.now()
        print(f"{inputcsv} Start time :{start_time}. End time :{end_time}")
print("The End! ----------")