from rasterio.plot import show
from rasterio.merge import merge
import rasterio as rio
import os
import sys
from pathlib import Path
import glob
from datetime import datetime
import platform

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
num_days = 365

root_folder = os.path.normpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LocationsList = ['Heino','Santana']
locationDict = {'Heino':['05m','1m'],'Santana':['1m']}
sourceList = ["GRASS GIS","SAGA GIS"]
for location in LocationsList:
    results_path = os.path.join(root_folder,'Results',location)
    for source in sourceList:
        # print(f'{source} starts')
        if source == "GRASS GIS":
            var_list = ["diff_rad", "glob_rad", "beam_rad", "refl_rad"]
            dict_list = {"glob_rad" : "global", "diff_rad" : "diffuse", "beam_rad": "direct", "refl_rad":"reflectance"}
        elif source == "SAGA GIS":
            var_list = ["Total Insolation", "Diffuse Insolation", "Direct Insolation","Duration of Insolation"]
            dict_list = {"Total Insolation" : "global", "Diffuse Insolation" : "diffuse", "Direct Insolation": "direct", "Duration of Insolation" : "duration"}
        else:
            print(f"Source {source}: is not available to process")
        resolution_list = locationDict[location]
        for resolution in resolution_list:
            results_path = os.path.join(root_folder,'Results',location,source)
            checkFolder(results_path)
            os.chdir(results_path)
            for var in var_list:
                print(f"{var} starts")
                outputVar = dict_list[var]
                raster_files = glob.glob(f"*{resolution}*{var}*.tif")
                if len(raster_files) == 0:
                    print(f'No files to process for {source} {outputVar}')
                    pass
                else:

                    raster_files.sort()
                    outputFile = f'{source}-{resolution}-{outputVar}.tif'
                    print(outputFile)

                    # Read metadata of first file
                    with rio.open(raster_files[0]) as src0:
                        meta = src0.meta
                        n_bands = src0.count
                    if n_bands == num_days:
                        print(f"No need to stack bands for {var}")
                        old_name = raster_files[0]
                        # os.remove(outputFile)
                        os.rename(old_name,outputFile)
                    else:
                        # Update meta to reflect the number of layers
                        # meta.update(count = len(raster_files)) # Original, works!
                        meta.update(count = num_days)
                        print("Bands data extracted")

                        # Read each layer and write it to stack
                        with rio.Env(CHECK_DISK_FREE_SPACE="NO"):
                            doy = 1
                            with rio.open(outputFile, 'w', **meta) as dst:
                                for id, layer in enumerate(raster_files, start=1):
                                    with rio.open(layer) as src1:
                                        for b in range(1,src1.count+1):
                                            if doy<=num_days:
                                                dst.write_band(doy, src1.read(b))
                                                doy += 1
                                            else:
                                                pass
                                        # dst.write_band(id, src1.read(1))
                        print(f'File {outputFile} was created at {datetime.now()}')