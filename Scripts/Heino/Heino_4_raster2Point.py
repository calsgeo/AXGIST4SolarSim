from osgeo import gdal
import os
from datetime import datetime
import sys
import pandas as pd
import json
import glob

print("Script starts")

script_folder = os.path.abspath(__file__)
data_folder = os.path.dirname(os.path.dirname(os.path.dirname(script_folder)))
data_subfolder = 'Input_Data'
location = 'Heino'
raster_input = 'outputRaster'
data_output = 'csv'
root_folder = os.path.join(data_folder,data_subfolder,location,raster_input)
os.chdir(root_folder)
print(root_folder)


def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    return [json.loads(gdf.to_json())['features'][0]['geometry']]

list_rasters = glob.glob(os.path.join(root_folder,'*.tif'))

# list_rasters = ["AHN3_05m_dtm_Heino"]
epsg_code = 28992

for inputRaster in list_rasters:
    if 'base_' in inputRaster:
        pass
    else:
        inputRaster = inputRaster.split('/')[-1]
        inputRaster = inputRaster.split('.')[0]

        current_time = datetime.now()
        print("    -----    ------   ")
        print(f"Start time for raster {inputRaster}: {current_time}")
        
        if "AHN3_05m" in inputRaster:
            dist_base = 1200
        elif "AHN3_1m" in inputRaster:
            dist_base = 1200
        elif inputRaster == "AHN4_05m_dsm_Heino":
            dist_base = 2500
        elif inputRaster == "AHN3_5m_dsm":
            dist_base = 20000
        else:
            dist_base = 100000

        # inDs = gdal.Open(f"/Volumes/Extreme SSD/Heino/DEM_Europe_10000m_InputDEM.tif")

        inDs = gdal.Open(os.path.join(root_folder,f"{inputRaster}.tif"))
        outputFile = os.path.join(data_folder,data_subfolder,location,data_output,f'{inputRaster}_Points.xyz')
        outputCSV = os.path.join(data_folder,data_subfolder,location,data_output,f'{inputRaster}_Points.csv')
        outputGEOJSON = os.path.join(data_folder,data_subfolder,location,'Vector',f'{inputRaster}_Points.geojson')

        outDs = gdal.Translate(outputFile, inDs, format='XYZ', creationOptions=["ADD_HEADER_LINE=YES"])
        outDs = None
        try:
            os.remove(outputCSV)
        except OSError:
            pass
        os.rename(outputFile, outputCSV)
        print("CVS file created")

        df = pd.read_csv(outputCSV, sep=" ")
        max_z = df["Z"].max()
        if max_z >8800:
            df = df[df["Z"] != max_z]
        df.to_csv(outputCSV,index=False)

        current_time = datetime.now()
        print(f"End time for raster {inputRaster}: {current_time}")