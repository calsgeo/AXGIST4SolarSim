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
LocationsList = ['Heino','Santana']
locationDict = {'Heino':['AHN_05m_dsm_1200m_InputDEM_WSTA_Updated.tif','AHN_1m_dsm_1200m_InputDEM_WSTA_Updated.tif'],'Santana':['geosampa_1m_dsm_124m_InputDEM_WSTA_Updated.tif']}
softwareFolder = 'saga-8.5.1_x64'

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
        software_path = os.path.join(root_folder,'Software',softwareFolder,'saga_cmd.exe')

        dem_path = os.path.join(input_path,inputDEM)

        linkePath = os.path.join(root_folder,'Input_Data',location,'outputRaster','Linke')

        svf = f"{location}_{resolution}_svf.tif"
        svf_path = os.path.join(rasterOutput,svf)

        for day in range(1,366):

            if day<=31:
                linke_value = 2.1
                linke_raster = os.path.join(linkePath,f"{location}_{resolution}_01_TL2010_Jan.tif")
            elif day<=59:
                linke_value = 2.2
                linke_raster = os.path.join(linkePath,f"{location}_{resolution}_02_TL2010_Feb.tif")
            elif day<=90:
                linke_value = 2.5
                linke_raster = os.path.join(linkePath,f"{location}_{resolution}_03_TL2010_Mar.tif")
            elif day<=120:
                linke_value = 2.9
                linke_raster = os.path.join(linkePath,f"{location}_{resolution}_04_TL2010_Apr.tif")
            elif day<=151:
                linke_value = 3.2
                linke_raster = os.path.join(linkePath,f"{location}_{resolution}_05_TL2010_May.tif")
            elif day<=181:
                linke_value = 3.4
                linke_raster = os.path.join(linkePath,f"{location}_{resolution}_06_TL2010_Jun.tif")
            elif day<=212:
                linke_value = 3.5
                linke_raster = os.path.join(linkePath,f"{location}_{resolution}_07_TL2010_Jul.tif")
            elif day<=243:
                linke_value = 3.3
                linke_raster = os.path.join(linkePath,f"{location}_{resolution}_08_TL2010_Aug.tif")
            elif day<=273:
                linke_value = 2.9
                linke_raster = os.path.join(linkePath,f"{location}_{resolution}_09_TL2010_Sep.tif")
            elif day<=304:
                linke_value = 2.6
                linke_raster = os.path.join(linkePath,f"{location}_{resolution}_10_TL2010_Oct.tif")
            elif day<=334:
                linke_value = 2.3
                linke_raster = os.path.join(linkePath,f"{location}_{resolution}_11_TL2010_Nov.tif")
            elif day<=366:
                linke_value = 2.3
                linke_raster = os.path.join(linkePath,f"{location}_{resolution}_12_TL2010_Dec.tif")
            else:
                linke_value = 2
                linke_raster = os.path.join(linkePath,f"{location}_{resolution}_TL2010_Year_gf.tif")

            day = str(day)
            # print day number
            print("The day number : " + str(day))
            # adjusting day num
            day = str(day).zfill(3)
            # day.rjust(3 + len(day), '0')
            # Initialize year
            year = "2022"
            # converting to date
            date = datetime.strptime(year + "-" + day, "%Y-%j").strftime("%Y-%m-%d")

            datetime2 = datetime.strptime(date, '%Y-%m-%d')

            day_str = calendar.day_name[datetime.weekday(datetime2)]

            directInsolation = os.path.join(rasterOutput,f"{location}_{resolution}_{day}_Direct Insolation.tif")
            diffuseInsolation = os.path.join(rasterOutput,f"{location}_{resolution}_{day}_Diffuse Insolation.tif")
            totalInsolation = os.path.join(rasterOutput,f"{location}_{resolution}_{day}_Total Insolation.tif")
            durationInsolation = os.path.join(rasterOutput,f"{location}_{resolution}_{day}_Duration of Insolation.tif")

            text = f'''
@ECHO OFF
PUSHD %~dp0
REM SET SAGA_TLB=C:\MyTools
SET SAGA_CMD="{software_path}"

REM Tool: Potential Incoming Solar Radiation

%SAGA_CMD% ta_lighting 2 ^
-GRD_DEM="{dem_path}" ^
-GRD_SVF="{svf_path}" ^
-GRD_LINKE="{linke_raster}" ^
-GRD_LINKE_DEFAULT={linke_value} ^
-GRD_DIRECT="{directInsolation}" ^
-GRD_DIFFUS="{diffuseInsolation}" ^
-GRD_TOTAL="{totalInsolation}" ^
-GRD_DURATION="{durationInsolation}" ^
-SOLARCONST=1367 ^
-LOCALSVF=1 ^
-UNITS=0 ^
-SHADOW=1 ^
-LOCATION="calculate from grid system" ^
-PERIOD=1 ^
-DAY="{date}" ^
-DAY_STOP="{date}" ^
-DAYS_STEP=1 ^
-HOUR_RANGE_MIN=0 ^
-HOUR_RANGE_MAX=24 ^
-HOUR_STEP=0.5 ^
-METHOD=3

PAUSE'''
            file = os.path.join(batPath,f"SAGA-{location}-{resolution}-{day}-SolarInsolation.bat")
            with open(file, 'w') as f:
                f.write(text)

print("Script Finishes")