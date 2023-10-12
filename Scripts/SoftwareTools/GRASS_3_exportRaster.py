#!/usr/bin/env python3
import grass.script as gscript
import os

def check_folder(folder):
    # Create a new directory because it does not exist
    isExist = os.path.exists(folder)
    if not isExist:
        os.makedirs(folder)
        print("The output directory is created!")

location = 'Santana' # options: 'Santana' and 'Heino'
resolution = '1m' # For Heino: '05m' or '1m'. For Santana: '1m'
absolute_path = 'Path_to_root_folder'
relative_path = os.path.join(absolute_path,'Results',location,'GRASS GIS')
check_folder(relative_path)

def raster_export(variable,i):
        day_value = str(i).zfill(3)
        raster_name =  location + "-" + resolution +  "-" + day_value + "-" + variable
        output_file= os.path.join(relative_path,raster_name+".tif")
        gscript.run_command("r.out.gdal",
        overwrite = True,
        input=raster_name,
        output = output_file,
        format="GTiff"
    )

if __name__ == '__main__':
    list_variables = ["diff_rad", "glob_rad", "beam_rad", "refl_rad"]
    for i in range(1,366):
        for variable in list_variables:
            raster_export(variable,i)