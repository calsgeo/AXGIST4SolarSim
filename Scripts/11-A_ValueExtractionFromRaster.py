import rasterio
import geopandas as gpd
import pandas as pd
import seaborn as sns
import os,sys
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def time_delta(time_start,message):
    time_finish = datetime.now()
    # get difference
    delta = time_finish - time_start
    sec = delta.total_seconds()
    (hours, sec) = divmod(sec, 3600)
    (minutes, sec) = divmod(sec, 60)
    formatted = f"{hours:02.0f}:{minutes:02.0f}:{sec:05.2f}"
    print(f'Time in {message}:', formatted)

def checkFolder(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        print(f"path {path} is created!")

time_start = datetime.now()

print(f"Script starts")

root_folder = os.path.normpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LocationsList = ['Heino','Santana']
locationResDict = {'Heino':['05m','1m'],'Santana':['1m']}
locationWSTADict = {'Heino':'INSPIRE_weatherLocation_28992.gml','Santana':'Santana_weatherStationLocation_31983.gml'}
sourceList = ["ArcGISPro","GRASS GIS","SAGA GIS"]

sourceListDict = {"ArcGISPro": ["global","direct","diffuse","directDuration"],"GRASS GIS":["global", "direct", "diffuse", "reflectance"],"SAGA GIS":["global", "direct", "diffuse"]}

for location in LocationsList:
    # Read points from Weather station
    weatherStation = os.path.join(root_folder,'Input_Data',location,'Vector',locationWSTADict[location])
    ws_location = gpd.read_file(weatherStation)
    ws_location = ws_location.explode(index_parts=False)
    coords = [(x,y) for x, y in zip(ws_location.geometry.x, ws_location.geometry.y)]
    resolution_list = locationResDict[location]
    for source in sourceList:
        for resolution in resolution_list:
            variables_list = sourceListDict[source]
            df = pd.DataFrame(columns=[variables_list], dtype=np.float32)
            results_path = os.path.join(root_folder,'Results',location,source)
            checkFolder(results_path)
            os.chdir(results_path)
            for var in variables_list:
                print(f'{location}: {source} - {resolution}, {var}')
                file = f"{source}-{resolution}-{var}.tif"
                isExist = os.path.exists(file)
                if not isExist:
                    pass
                else:
                    src = rasterio.open(file)
                    for val in src.sample(coords):
                        for idx,v in enumerate(val):
                            df.at[idx, var] = v
                    if source == "SAGA GIS":
                        df[var] = df[var] * 1000
            if len(df)>0:
                df["resolution"] = resolution
                df = df.reset_index(drop=True)
                df = df.rename(columns={"index":"doy"})
                df["doy"] = df.index + 1
                output_folder = os.path.join(root_folder,'Results',location,'csv')
                checkFolder(output_folder)
                df.to_csv(os.path.join(output_folder,f'{source}-{resolution}-SimulationResults.csv'))
                print(f"Results Export for {location}: {source}, with resolution {resolution}")
            else:
                pass