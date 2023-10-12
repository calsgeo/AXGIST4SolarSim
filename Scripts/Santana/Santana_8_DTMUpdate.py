### Uses the rasterio library and a input location to update the value of the cell at that location
import rasterio
from rasterio.plot import reshape_as_raster, reshape_as_image
import os
import sys
from datetime import datetime
import geopandas as gpd

script_folder = os.path.abspath(__file__)
data_folder = os.path.normpath(os.path.dirname(os.path.dirname(os.path.dirname(script_folder))))
print(data_folder)
sys.exit()
data_subfolder = 'Input_Data'
location = 'Santana'
csv_input = 'csv'
raster_input = 'outputRaster'
vector_input = 'Vector'
root_folder = os.path.join(data_folder,data_subfolder,location)
os.chdir(root_folder)

originalRaster = "geosampa_1m_dsm_124m_InputDEM.tif"
raster_file = os.path.join(root_folder,raster_input,originalRaster)
newRaster = f"{raster_file.split('.')[0]}_WSTA_Updated.tif"
crs = rasterio.crs.CRS({"init": "epsg:31983"})
weatherStation = os.path.join(root_folder,vector_input,"Santana_weatherStationLocation_31983.gml")
ws_location = gpd.read_file(weatherStation,driver='GML')
ws_location = ws_location.explode(index_parts=False)
east,north = ws_location.geometry.x[0], ws_location.geometry.y[0]
coords = [(east,north)]

print(datetime.now())
# open the raster dataset
with rasterio.open(raster_file) as dataset:
    # Get pixel coordinates from map coordinates
    px, py = dataset.index(east, north)
    print('Pixel Y, X coords: {}, {}'.format(py, px))
    # read the data into a numpy array
    data = dataset.read(1)
    for val in dataset.sample(coords):
        height_base = 802.78

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