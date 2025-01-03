import rasterio
from rasterio.plot import show
from rasterio.plot import show_hist
from rasterio.mask import mask
from rasterio.fill import fillnodata
from shapely.geometry import box
import geopandas as gpd
from fiona.crs import from_epsg
import pycrs
import sys
import os
import numpy as np
import glob

print("Script starts")

script_folder = os.path.abspath(__file__)
data_folder = os.path.dirname(os.path.dirname(os.path.dirname(script_folder)))
data_subfolder = 'Input_Data'
location = 'Santana'
source = 'Geosampa' # Two options available: AHN and DEM-Copernicus
root_folder = os.path.join(data_folder,data_subfolder,location)
os.chdir(root_folder)
raster_folder = os.path.join(root_folder,'baseRaster')

def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]


list_rasters = glob.glob(os.path.join(raster_folder,'*.tif'))
weatherStation = os.path.join(root_folder,"Vector","Santana_weatherStationLocation_31983.gml")
shape_file = gpd.read_file(weatherStation,driver='GML')

for inputRaster in list_rasters:
    inputRaster = inputRaster.split('/')[-1]
    print(f"------ Input raster file: {inputRaster}")
    
    dist_base = 124
    env_shape_file = shape_file.buffer(dist_base).envelope
    out_clipped_tif = os.path.join(root_folder,'outputRaster',f"{inputRaster.split('.')[0]}_{dist_base}m_InputDEM.tif")

    data = rasterio.open(os.path.join(raster_folder,inputRaster))
    coords = getFeatures(env_shape_file)
    out_img, out_transform = mask(dataset=data, shapes=coords, crop=True, nodata=np.nan)
    # Copy the metadata
    out_meta = data.meta.copy()
    # Parse EPSG code
    epsg_code = int(data.crs.data['init'][5:])
    crs = rasterio.crs.CRS.from_epsg(epsg_code)

    out_meta.update({"driver": "GTiff",
                    "height": out_img.shape[1],
                    "width": out_img.shape[2],
                    "transform": out_transform,
                    "dtype": "float32"
                    # "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()
                    })

    with rasterio.open(out_clipped_tif, "w", **out_meta) as dest:
        # for i in range(1, data.count)
        dest.crs = crs
        dest.write(out_img)

    clipped = rasterio.open(out_clipped_tif)
    print("End clipping")