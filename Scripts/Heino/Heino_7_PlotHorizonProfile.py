import math
import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt
import os
from datetime import datetime
import random
import glob

script_folder = os.path.abspath(__file__)
data_folder = os.path.normpath(os.path.dirname(os.path.dirname(os.path.dirname(script_folder))))
data_subfolder = 'Input_Data'
location = 'Heino'
csv_input = 'csv'
raster_input = 'outputRaster'
vector_input = 'Vector'
root_folder = os.path.join(data_folder,data_subfolder,location)

type_graph = "-" # Definition of the range of distances from the weather station. Option is manual
var = "elevation_pyproj" # Elevation column

# os.chdir(root_folder)
def plot_data(df,number):
    angles = list(range(-180,180,number))
    col = f'azimuth_pyproj_class360_{number}'
    df[col] = 0
    for a in angles:
        df["control_col"] = df.azimuth_hor
        df[col] = np.where(df["azimuth_hor"]<= a,int(a),df[col])
        df["azimuth_hor"] = np.where(df["azimuth_hor"]<= a,9999,df["azimuth_hor"])
    df[col].astype('int')
    df_agg = df.groupby([col], sort=False)[var].min().reset_index()
    df_agg = df_agg.astype({col: "int",var:'float'})
    df_agg = df_agg.sort_values(by=[col], ascending=True)
    return df_agg,col

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

listFolders = glob.glob(os.path.join(root_folder,csv_input,'*/'))

for folder in listFolders:
    demFile = folder.split(os.sep)[-2]
    hor_folder = os.path.join(folder,'hor')
    if "AHN_05m" in demFile:
      minDistance,dist_base,interval,rasterName = 100,1200,100,"AHN3 0.5m"
    elif "AHN_1m" in demFile:
      minDistance,dist_base,interval,rasterName = 100,1200,100,"AHN3 1m"
    elif "AHN_5m" in demFile:
      minDistance,dist_base,interval,rasterName = 3000,20000,1500,"AHN3 5m"
    elif "DEM_Europe" in demFile:
      minDistance,dist_base,interval,rasterName = 3500,100500,10000,"Copernicus 25m"
    else:
       print(f'There are none parameters defined for file {demFile}')
    
    # create a figure and a subplot
    fig, ax = plt.subplots()
    colormap = plt.cm.cool

    # create a list of colors from the colormap
    colors = [colormap(i) for i in range(colormap.N-1,0,-1)]
    time_start = datetime.now()
    print(f'starting time for file {demFile}: {time_start}')
    # folder_hor = os.path.join(root_folder,"output",f"{inputRaster}","hor")

    times = 11 # Number of steps in the horizon plot

    if type_graph == "manual":
        minDistance = 3500
        maxDistance = 30000
        # listDistances = list(np.arange(minDistance, maxDistance+minDistance ,minDistance))
        listDistances = [minDistance,6000,9000,12000,15000,18000,21000,24000,27000,maxDistance]
        listDistances.sort(reverse=True)
    else:
        maxDistance = dist_base
        print(f'MaxiDistance : {maxDistance}')
        print(f'dist_base : {dist_base}')
        listDistances = list(np.arange(minDistance, maxDistance ,interval))
        print(f'Tamano de la lista de distancias: {len(listDistances)}')
        listDistances.sort(reverse=True)
        if maxDistance > dist_base:
            maxDistance = dist_base
            listDistances[0] = dist_base

    print(f"Distances for the plot: {listDistances}")
    
    angle_interval = 5 # For the plot output

    title = f"Horizon profile using {rasterName} \n"
    fig = plt.figure(figsize=(8, 8))
    plt.rcParams.update({'font.size': 10})
    ax = fig.add_subplot(1,1,1, polar=True)
    plt.setp(ax.get_yticklabels(), fontweight="bold")
    ax.set_ylim(78, 91) # To convert from Sky view to Horizon view
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    # Reads HOR file
    csv_file = os.path.join(hor_folder,f'{demFile}_Points_Calc_ProfileData_Distance_{dist_base}m.hor')
    df_csv = pd.read_csv(csv_file)
    df_csv['elevation_pyproj'] = 90-df_csv['elevation_pyproj'].values # To convert from Sky view to Horizon view
    df_agg,colname = plot_data(df_csv,angle_interval)
    df_agg.to_csv(os.path.join(hor_folder,f'{demFile}_radarPlotData_distance_full.csv'),index=False)

    N = len(df_agg[colname])
    angles = [n / float(N) * 2 * math.pi for n in range(N)]
    angles += angles[:1]

    label_loc = np.linspace(start=0, stop=2 * np.pi, num=len(df_agg[colname]))
    plt.xticks(angles[:-1], df_agg[colname], size=9, color='dimgray')

    values=df_agg[var].values.flatten().tolist()
    values += values[:1]

    ax.plot(angles, values, label=f"> {maxDistance}m", color = colors[0], linewidth=1)

    idx_colour = len(colors)/(times+1)
    for idx, dist in enumerate(listDistances):
        print(f"Plot horizon at {dist}")
        csv_file = os.path.join(hor_folder,f"{demFile}_Points_Calc_ProfileData_Distance_{dist}m.hor")
        df_csv = pd.read_csv(csv_file)
        df_csv['elevation_pyproj'] = 90-df_csv['elevation_pyproj'].values # To convert from Sky view to Horizon view
        df_agg,colname = plot_data(df_csv,angle_interval)
        df_agg.to_csv(os.path.join(hor_folder,f'{demFile}_radarPlotData_distance_{dist}.csv'),index=False)
        values=df_agg[var].values.flatten().tolist()
        values += values[:1]
        ax.plot(angles , values, label=f"< {dist}m", color = colors[int(np.floor(idx*(idx_colour+1)))], linewidth=1)

    ax.tick_params(axis='x', rotation=0)
    ax.xaxis.grid(linestyle="--", alpha=0.4)
    ax.set_rlabel_position(30)
    angle = np.deg2rad(93)
    # ax.legend(loc="lower left", bbox_to_anchor=(0.9,0.9), ncol=3)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5,-0.15), ncol=6, columnspacing=0.4)

    plt.title(title, fontsize = 18, x=0.5, y=1.0)
    outputFolder = os.path.join(data_folder,'Results','plots')
    plt.savefig(os.path.join(outputFolder,f"{demFile}_{minDistance}m-{maxDistance}m_horizon.png"),dpi=300,bbox_inches='tight', transparent=True)
    time_end = datetime.now()
    print(f'End time for file {demFile}: {time_end}')
print("The end!")