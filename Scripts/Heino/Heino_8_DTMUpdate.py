### Uses the rasterio library and a input location to update the value of the cell at that location
import rasterio
from rasterio.plot import reshape_as_raster, reshape_as_image
import os
import sys
from datetime import datetime
import geopandas as gpd

script_folder = os.path.abspath(__file__)
data_folder = os.path.dirname(os.path.dirname(os.path.dirname(script_folder)))
data_subfolder = 'Input_Data'
location = 'Heino'
csv_input = 'csv'
raster_input = 'outputRaster'
vector_input = 'Vector'
root_folder = os.path.join(data_folder,data_subfolder,location)
os.chdir(root_folder)

originalRaster = ["AHN_05m_dsm_1200m_InputDEM.tif","AHN_1m_dsm_1200m_InputDEM.tif"]
weatherStation = os.path.join(root_folder,vector_input,"INSPIRE_weatherLocation_28992.gml")
ws_location = gpd.read_file(weatherStation,driver='GML')
ws_location = ws_location.explode(index_parts=False)
east,north = ws_location.geometry.x[0], ws_location.geometry.y[0]
coords = [(east,north)]

for raster in originalRaster:
    raster_file = os.path.join(root_folder,raster_input,raster)
    newRaster = f"{raster_file.split('.')[0]}_WSTA_Updated.tif"
    crs = rasterio.crs.CRS({"init": "epsg:28992"})

    print(datetime.now())
    # open the raster dataset
    with rasterio.open(raster_file) as dataset:
        # Get pixel coordinates from map coordinates
        px, py = dataset.index(east, north)
        print('Pixel Y, X coords: {}, {}'.format(py, px))
        # read the data into a numpy array
        data = dataset.read(1)
        for val in dataset.sample(coords):
            height_base = round(val[0]+ 1.5,2)

        # replace the value at a specific location
        data[px, py] = height_base
        profile = dataset.profile
        meta = dataset.meta

        print(profile)
        print(meta)
        with rasterio.open(newRaster, 'w', **profile) as dst:
            dst.crs = crs
            dst.write(data,1)
    print(datetime.now())
print("the end")