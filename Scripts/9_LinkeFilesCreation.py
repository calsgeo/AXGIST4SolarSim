import rasterio
import geopandas as gpd
import pandas as pd
import sys,os
import matplotlib.pyplot as plt
from rasterio import features
from rasterio.enums import MergeAlg
from rasterio.plot import show
import numpy as np
from rasterio.crs import CRS
from datetime import datetime
import glob

def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]

def time_delta(time_start,message):
    time_finish = datetime.now()
    # get difference
    delta = time_finish - time_start
    sec = delta.total_seconds()
    (hours, sec) = divmod(sec, 3600)
    (minutes, sec) = divmod(sec, 60)
    formatted = f"{hours:02.0f}:{minutes:02.0f}:{sec:05.2f}"
    print(f'Time in {message}:', formatted)

def check_folder(folder):
    # Create a new directory because it does not exist
    isExist = os.path.exists(folder)
    if not isExist:
        os.makedirs(folder)
        print("The output directory is created!")

start_time = datetime.now()
current_time = start_time
print("    -----    ------   ")
print(f"start for Linke raster files creation")

script_folder = os.path.abspath(__file__)
data_folder = os.path.normpath(os.path.dirname(os.path.dirname(script_folder)))
data_subfolder = 'Input_Data'
linke_folder = 'Tl2010_MonthlyAv_and_YearlyAv_WGS84_GeoTIFF'
linkeFiles_path = os.path.join(data_folder,data_subfolder,linke_folder)
raster_input = 'outputRaster'
csv_input = 'csv'


locations = ['Santana']
for location in locations:
    root_folder = os.path.join(data_folder,data_subfolder,location)
    os.chdir(root_folder)
    if location == "Santana":
        epsg_code = 31983
        resolutions = ['1m']
        coords_file = ['geosampa_1m_dsm_124m_InputDEM_Points.csv']
        dem_file = ["geosampa_1m_dsm_124m_InputDEM_WSTA_Updated.tif"]
        
    else:
        epsg_code = 28992
        resolutions = ['1m','05m']
        coords_file = ['AHN_05m_dsm_1200m_InputDEM_Points.csv','AHN_1m_dsm_1200m_InputDEM_Points.csv']
        dem_file = ["AHN_05m_dsm_1200m_InputDEM_WSTA_Updated.tif","AHN_1m_dsm_1200m_InputDEM_WSTA_Updated.tif"]
    
    # Linke
    list_files = glob.glob(os.path.join(linkeFiles_path,'*.tif'))
    list_Linkefiles = [i.split("/")[-1] for i in list_files]
    linke_dic = {"TL2010_Jan_gf.tif":"01","TL2010_Feb_gf.tif":"02","TL2010_Mar_gf.tif":"03","TL2010_Apr_gf.tif":"04","TL2010_May_gf.tif":"05","TL2010_Jun_gf.tif":"06","TL2010_Jul_gf.tif":"07","TL2010_Aug_gf.tif":"08","TL2010_Sep_gf.tif":"09","TL2010_Oct_gf.tif":"10","TL2010_Nov_gf.tif":"11","TL2010_Dec_gf.tif":"12","TL2010_Year_gf.tif":"13"}

    for idx,res in enumerate(resolutions):
        current_time = datetime.now()
        print(f'{location} with resolution {res}')
        for cFile in coords_file:
            for dFile in dem_file:
                if res in cFile:
                    inputPoints = os.path.join(root_folder,csv_input,cFile)
                    if res in dFile:
                    ## Read raster files
                        # DEM
                        dem_path = os.path.join(root_folder,raster_input,dFile)
                        print(dem_path)
                        raster = rasterio.open(dem_path)
                        rasterCrs = CRS.from_epsg(epsg_code)
                        # Read points coordinates
                        df = pd.read_csv(inputPoints)
                        pts = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["X"],df["Y"]), crs=f"EPSG:{epsg_code}")
                        pts = pts.to_crs(4326)
                        coords = [(x,y) for x, y in zip(pts.geometry.x, pts.geometry.y)]
                        time_delta(current_time,"Points location reading")
                        current_time = datetime.now()
                        outputPath = os.path.join(root_folder,raster_input,"Linke")
                        check_folder(outputPath)
                        
                        # Sample the raster at  point location and store the values in a DataFrame
                        for linke in list_Linkefiles:
                            linke = linke.split(os.sep)[-1]
                            mm = linke_dic[linke]
                            src = rasterio.open(os.path.join(linkeFiles_path,linke))
                            srcCrs = src.crs
                            values = src.sample(coords)
                            list_values = []
                            for val in values:
                                for v in val:
                                    list_values.append(v)
                            list_values = [x / 20 for x in list_values]
                            linke = linke.replace("_gf.tif", "")
                            pts[linke] = list_values
                            pts = pts.to_crs(epsg_code)
                            pts['x'] = pts.geometry.x
                            pts['y'] = pts.geometry.y

                            # create tuples of geometry, value pairs, where value is the attribute value you want to burn
                            geom_value = ((geom,value) for geom, value in zip(pts.geometry, pts[linke]))
                            
                            # Rasterize vector using the shape and transform of the raster
                            rasterized = features.rasterize(geom_value,
                                                            out_shape = raster.shape,
                                                            transform = raster.transform,
                                                            all_touched = True,
                                                            fill = np.nan,   # background value
                                                            merge_alg = MergeAlg.replace,
                                                            default_value = 1,
                                                            dtype = np.float32)
                            with rasterio.open(
                                os.path.join(outputPath,f"{location}_{res}_{mm}_{linke}.tif"),
                                "w",
                                driver = "GTiff",
                                transform = raster.transform,
                                dtype = rasterio.float32,
                                crs = rasterCrs,
                                count = 1,
                                width = raster.width,
                                height = raster.height) as dst:
                                dst.write(rasterized, indexes = 1)

                            time_delta(current_time,f"File {linke} created")
                            current_time = datetime.now()                

        time_delta(start_time,f"{datetime.now()} - Script Ends ")
        print("    -----    ------   ")