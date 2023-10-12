import rasterio
import geopandas as gpd
import pandas as pd
import seaborn as sns
import os,sys
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import glob
import re

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

root_folder = os.path.normpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LocationsList = ['Heino','Santana']
# locationFilesDict = {'Heino':'Heino_CityGML.gml','Santana':'Santana_CityGML.gml'}
sourceList = ["CitySim","Ladybug","SimStadt"]
for location in LocationsList:
    outputFolder = os.path.join(root_folder,'Results',location,'csv')
    for source in sourceList:
        inputLocation = os.path.join(root_folder,'Results',location,source)
        if source== 'SimStadt':
            inputFile = f'{location}_CityGML_meteonorm_Heino_SRA_SW.out'
            inputPath = os.path.join(inputLocation,inputFile)
            # print(inputLocation)
            list_files = glob.glob(inputPath)
            if len(list_files)==0:
                print(f'{inputFile} is not available')
                pass
            else:
                print(f'{location} {source}')
                df = pd.read_csv(inputPath, sep="\t")
                weather_cols = [col for col in df.columns if 'WeatherStationHeino' in col]
                df_ws = df[weather_cols]
                max_value = 0
                roof_column = ""
                for col in weather_cols:
                    sum_col = df_ws[col].sum()
                    if sum_col>max_value:
                        max_value = sum_col
                        roof_column = col
                df_ws_day = df_ws.groupby(df_ws.index // 24).sum()
                df_ws_day = df_ws_day.reset_index(drop=True)
                df_ws_test = df_ws_day.copy()
                list_surfaces = df_ws_test.columns.values.tolist()
                df_ws_day.rename(columns={list_surfaces[0]:"WallSurface_1"
                                        ,list_surfaces[1]:"WallSurface_2"
                                        ,list_surfaces[2]:"WallSurface_3"
                                        ,list_surfaces[3]:"WallSurface_4"
                                        ,list_surfaces[4]:"RoofSurface"}, inplace=True)
                df_ws_day["doy"] = df_ws_day.index + 1
                outputFile = os.path.join(outputFolder,"SimStadt-1m-SimulationResults.csv")
                print(f'Output file {outputFile} created')
                df_ws_day.to_csv(outputFile,index=False)
        elif source== 'CitySim':
            print(f'{location} {source}')
            inputFile = f'{location}_statusQuo_CitySim_input_Bldgs_SW.out'
            
            inputPath = os.path.join(inputLocation,inputFile)
            list_files = glob.glob(inputPath)
            if len(list_files)==0:
                print(f'{inputFile} is not available')
                pass
            else:
                out_df = pd.read_csv(inputPath,  sep='\t') # change file name
                ir_cols = [col for col in out_df.columns if 'WeatherStationHeino' in col or 'Polygon' in col]
                ir_df = pd.read_csv(inputPath,  sep='\t', usecols=ir_cols)

                # Change column names
                old_name = []
                new_name = []
                for column in ir_df:
                    old_name.append(column)
                for i in old_name:
                    result = re.search(r'\((.*)\):Irra', i)
                    new_name.append(result.group(1))
                ir_df.columns = new_name
                # Change column names
                old_name = []
                new_name = []
                for column in ir_df:
                    old_name.append(column)
                for i in old_name:
                    result = re.search(r'\((.*)', i)
                    new_name.append(result.group(1))
                ir_df.columns = new_name

                list_surfaces = list(ir_df.columns)
                df_surfaces = pd.DataFrame(list_surfaces, columns = ['surface_id'])

                ir_df = ir_df.rename(columns={
                    'Polygon_UUID_6aa16f83-b982-4e79-b40a-142795a13a4a':'RoofSurface',
                    'Polygon_UUID_24aa16f0-4bbb-4e88-948a-5113836134c6':'WallSurface_S',
                    'Polygon_UUID_b5df9cc8-fcbd-49c5-944f-36e250397d1d':'WallSurface_W',
                    'Polygon_UUID_c4693f06-a25e-44a7-8d37-718f7cc6d771':'WallSurface_N',
                    'Polygon_UUID_14050b6a-e2cd-40e5-8091-34b10d59acfd':'WallSurface_E'
                    })
                ir_df_day = ir_df.groupby(ir_df.index // 24).sum()
                ir_df_day = ir_df_day.round(3)
                ir_df_day["doy"] = ir_df_day.index + 1


                outputFile = os.path.join(outputFolder,f"{source}-1m-SimulationResults.csv")
                current_time = datetime.now()
                time_delta(current_time,f"File {inputFile} processed")
                current_time = datetime.now()
                print(f'Output file {outputFile} created')
                ir_df_day.to_csv(outputFile,index=False)
        elif source== 'Ladybug':
            print(f'{location} {source}')
            inputFile = f'{location}_Ladybug_ExportResults.csv'
            inputPath = os.path.join(inputLocation,'-'+inputFile)
            list_files = glob.glob(inputPath)
            if len(list_files)==0:
                print(inputPath)
                print(f'{inputFile} is not available')
                pass
            else:
                df = pd.read_csv(inputPath,header=None)
                solar_values = list(df[df.columns[0]].values)
                surfaces_list = ['GroundSurface','WallSurface_UUID_0aaf7b44-4fab-42b0-aaa7-380113caeea0','WallSurface_UUID_2ae98dca-a3b6-4890-a768-3bde754de4cb','WallSurface_UUID_1642fc1e-bbb4-49e9-b47d-881a3cf30be4','WallSurface_UUID_6e4f3933-7da7-446f-b8c2-6627879112b9','RoofSurface']
                num_surfaces = len(surfaces_list)
                num_minutes = 8760
                data = {}
                list_0 = []
                list_1 = []
                list_2 = []
                list_3 = []
                list_4 = []
                list_5 = []
                for x in range(0,len(solar_values),num_surfaces):
                    list_0.append(solar_values[x])
                    list_1.append(solar_values[x+1])
                    list_2.append(solar_values[x+2])
                    list_3.append(solar_values[x+3])
                    list_4.append(solar_values[x+4])
                    list_5.append(solar_values[x+5])

                    data[surfaces_list[0]] = list_0
                    data[surfaces_list[1]] = list_1
                    data[surfaces_list[2]] = list_2
                    data[surfaces_list[3]] = list_3
                    data[surfaces_list[4]] = list_4
                    data[surfaces_list[5]] = list_5

                    df_minute = pd.DataFrame.from_dict(data)
                    df_day = df_minute.groupby(df_minute.index // 24).sum()
                    df_day = df_day.multiply(1000)
                    df_day["doy"] = df_day.index + 1

                    outputFile = os.path.join(outputFolder,f"{source}-1m-SimulationResults.csv")
                    current_time = datetime.now()
                    time_delta(current_time,f'Output file {outputFile} created')
                    df_day.to_csv(outputFile,index=False)