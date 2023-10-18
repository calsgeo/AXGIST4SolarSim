# This file needs to be placed at d:/Heino
import os,sys
import datetime
import arcpy
import sys

def check_folder(folder):
    # Create a new directory because it does not exist
    isExist = os.path.exists(folder)
    if not isExist:
        os.makedirs(folder)
        print("The output directory is created!")

def time_delta(time_start,message):
    time_finish = datetime.datetime.now()
    # get difference
    delta = time_finish - time_start
    sec = delta.total_seconds()
    mins = sec / 60
    hours = mins /60
    # print(f'Time in {message}:', hours, mins)
    print('Time in ', message, ' : ', hours, ' : ', mins)

script_path = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
root_folder = os.path.normpath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
data_subfolder = 'Input_Data'
location = 'Heino'
data_folder = os.path.join(root_folder,data_subfolder,location)
os.chdir(data_folder)
    
outputPath = os.path.join(root_folder,'Results',location,'ArcGISPro')
check_folder(outputPath)

arcpy.env.workspace = outputPath
arcpy.env.overwriteOutput = True
month= "full"
start_time = datetime.datetime.now()
print("    -----    ------   ")
if location == 'Heino':
    dems = ['AHN_05m_dsm_1200m_InputDEM_WSTA_Updated.tif','AHN_1m_dsm_1200m_InputDEM_WSTA_Updated.tif']
    latitude = 52.434561675532
elif location == 'Santana':
    dems = ['geosampa_1m_dsm_124m_InputDEM_WSTA_Updated.tif']
    latitude = -23.4964207730796
else:
    print('New location, You need to set up the DWM file names')
    sys.exit()


skySize = 200
dayInterval = 1
hourInterval = 0.5
zFactor = 1
calcDirections = 8
zenithDivisions = 8
azimuthDivisions = 8
diffuseProp = 0.3
transmittivity = 0.5

if month == "january":
    monthNumber = "01"
    start_day,end_day = 1,32
elif month == "february":
    monthNumber = "02"
    start_day,end_day = 32,60
elif month == "march":
    monthNumber = "03"
    start_day,end_day = 60,91
elif month == "april":
    monthNumber = "04"
    start_day,end_day = 91,121
elif month == "may":
    monthNumber = "05"
    start_day,end_day = 121,152
elif month == "june":
    monthNumber = "06"
    start_day,end_day = 152,182
elif month == "july":
    monthNumber = "07"
    start_day,end_day = 182,213
elif month == "august":
    monthNumber = "08"
    start_day,end_day = 213,244
elif month == "september":
    monthNumber = "09"
    start_day,end_day = 244,274
elif month == "october":
    monthNumber = "10"
    start_day,end_day = 274,305
elif month == "november":
    monthNumber = "11"
    start_day,end_day = 305,335
elif month == "december":
    monthNumber = "12"
    start_day,end_day = 335,1
elif month == "full":
    monthNumber = "365"
    start_day,end_day = 1,366
elif month == "firstSemester":
    monthNumber = "00A"
    start_day,end_day = 1,189
elif month == "secondSemester":
    monthNumber = "00B"
    start_day,end_day = 189,366
else:
    monthNumber = "999"
    start_day,end_day = 350,1

for dem_file in dems:

    input_dem = os.path.join(data_folder,'outputRaster',dem_file)
    resolution = dem_file.split('_')[1]
    source = dem_file.split('_')[0]
    print("Start time ", month," - resolution ", resolution, " : ", start_time)

    direct_rad = os.path.join(outputPath, monthNumber + "-" + source + "-" + resolution+"-direct_rad.tif")
    diff_rad = os.path.join(outputPath,monthNumber + "-" + source + "-" + resolution+"-diff_rad.tif")
    direct_duration = os.path.join(outputPath, monthNumber + "-" + source + "-" + resolution+"-direct_duration.tif")
    glob_rad = os.path.join(outputPath, monthNumber + "-" + source + "-" + resolution+"-global_rad.tif")


    out_global_radiation_raster = arcpy.sa.AreaSolarRadiation(
        input_dem,
        latitude,
        skySize,
        f"MultiDays 2020 {start_day} {end_day}",
        dayInterval,
        hourInterval,
        "INTERVAL",
        zFactor,
        "FROM_DEM",
        calcDirections,
        zenithDivisions,
        azimuthDivisions,
        "Standard overcast sky",
        diffuseProp,
        transmittivity,
        direct_rad,
        diff_rad,
        direct_duration)
    out_global_radiation_raster.save(glob_rad)
    time_delta(start_time,f"End Time  {month}, {start_time} - Total Time:")