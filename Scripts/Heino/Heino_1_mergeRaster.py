from rasterio.plot import show
from rasterio.merge import merge
import rasterio as rio
import os
import sys
from pathlib import Path
import glob


# Relative path preparation #

script_folder = os.path.abspath(__file__)
data_folder = os.path.dirname(os.path.dirname(os.path.dirname(script_folder)))
data_subfolder = 'Input_Data'
location = 'Heino'
source = 'AHN' # Two options available: AHN and DEM-Copernicus
output_folder = 'baseRaster'

if source == 'AHN':
    resolution = ['05m','5m']
else:
    resolution = ['20m']

output_path = os.path.join(data_folder,data_subfolder,location,output_folder)

for res in resolution:
    base_path = os.path.join(data_folder,data_subfolder,location,source,res)
    os.chdir(base_path)
    output_file = os.path.join(output_path,f"{source}_{res}_dsm.tif")

    raster_files = glob.glob("*.TIF")
    raster_to_mosiac = []

    for p in raster_files:
        raster = rio.open(p)
        raster_to_mosiac.append(raster)

    mosaic, output = merge(raster_to_mosiac)

    output_meta = raster.meta.copy()
    output_meta.update(
        {"driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": output,
        }
    )

    with rio.open(output_file, "w", **output_meta) as m:
        m.write(mosaic)

    print("raster merging complete")