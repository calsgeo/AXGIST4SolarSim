import os,sys
from datetime import datetime
from datetime import date
import calendar

def checkFolder(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        print(f"path {path} is created!")

print("Script starts")
script_path = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
root_folder = os.path.normpath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
softwareFolder = 'saga-8.5.1_x64'
LocationsList = ['Heino','Santana']
locationDict = {'Heino':['AHN_05m_dsm_1200m_InputDEM_WSTA_Updated.tif','AHN_1m_dsm_1200m_InputDEM_WSTA_Updated.tif'],'Santana':['geosampa_1m_dsm_124m_InputDEM_WSTA_Updated.tif']}
for location in LocationsList:
    input_path = os.path.join(root_folder,'Input_Data',location,'outputRaster')
    results_path = os.path.join(root_folder,'Results',location,'SAGA GIS')
    checkFolder(results_path)
    os.chdir(results_path)

    listDems = locationDict[location]
    for inputDEM in listDems:
        resolution = inputDEM.split("_")[1]
        batPath = os.path.join(results_path,"bat")
        checkFolder(batPath)
        rasterOutput = results_path
        checkFolder(rasterOutput)

        resolution = inputDEM.split("_")[1]
        visible = f"{location}_{resolution}_visible.tif"
        svf = f"{location}_{resolution}_svf.tif"
        simple = f"{location}_{resolution}_simple.tif"
        terrain = f"{location}_{resolution}_terrain.tif"
        distance = f"{location}_{resolution}_distance.tif"

        dem_path = os.path.join(input_path,inputDEM)
        visible_path = os.path.join(rasterOutput,visible)
        svf_path = os.path.join(rasterOutput,svf)
        simple_path = os.path.join(rasterOutput,simple)
        terrain_path = os.path.join(rasterOutput,terrain)
        distance_path = os.path.join(rasterOutput,distance)

        software_path = os.path.join(root_folder,'Software',softwareFolder,'saga_cmd.exe')

        text = f'''
@ECHO OFF

PUSHD %~dp0

REM SET SAGA_TLB=C:\MyTools

SET SAGA_CMD={software_path}

REM Tool: Sky View Factor

%SAGA_CMD% ta_lighting 3 ^
-DEM="{dem_path}" ^
-VISIBLE="{visible_path}" ^
-SVF="{svf_path}" ^
-SIMPLE="{simple_path}" ^
-TERRAIN="{terrain_path}" ^
-DISTANCE="{distance_path}" ^
-RADIUS=0 ^
-NDIRS=8 ^
-METHOD=1 ^
-DLEVEL=3

PAUSE
        '''
        file = os.path.join(batPath,f"{location}-{resolution}-SkyFactor.bat")
        print(file)
        with open(file, 'w') as f:
            f.write(text)

print("Script Finishes")