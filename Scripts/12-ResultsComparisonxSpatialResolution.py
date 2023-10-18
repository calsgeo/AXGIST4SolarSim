import pandas as pd
import seaborn as sns
import os,sys
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import glob

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
locationList = ['Heino']
sources = ["ArcGISPro","GRASS GIS","SAGA GIS"]
list_variables = ["global","direct","diffuse"]

for location in locationList:
    weatherFolder = os.path.join(root_folder,'Input_Data',location,'WeatherData')
    outputFolder = os.path.join(root_folder,'Results','plots')
    checkFolder(outputFolder)
    if location == 'Heino':
        weatherFileName = "NLD_OV_Heino.062780_TMYx.2007-2021.csv"
    else:
        weatherFileName = "NLD_OV_Heino.062780_TMYx.2007-2021.csv"
    weatherFilePath = os.path.join(weatherFolder,weatherFileName)
    list_files = glob.glob(weatherFilePath)
    if len(list_files)==0:
        pass
    else:
        df_ws = pd.read_csv(weatherFilePath)
        df_ws_doy = df_ws[['GHI (W/m^2)','DNI (W/m^2)','DHI (W/m^2)']].groupby(df_ws.index // 24).sum()
        df_ws_doy = df_ws_doy.reset_index()
        df_ws_doy = df_ws_doy.rename(columns={"index":"doy"})
        df_ws_doy["doy"] = df_ws_doy.index + 1
        df_ws_doy["source"] = "OneBuilding"
        df_ws_doy = df_ws_doy.rename(columns={'GHI (W/m^2)':"global",'DNI (W/m^2)':"direct",'DHI (W/m^2)':"diffuse"})
        df_ws_doy["RoofSurface"] = df_ws_doy["global"]

        fontBase = 40
        sns.set( rc = {'figure.figsize' : ( 30, 10 )}, style='whitegrid')
        for variable in list_variables:
            for source in sources:
                input_folder = os.path.join(root_folder,'Results',location,'csv')
                df_05m = pd.read_csv(os.path.join(input_folder,f'{source}-05m-SimulationResults.csv'))
                df_1m = pd.read_csv(os.path.join(input_folder,f'{source}-1m-SimulationResults.csv'))
                df = pd.concat([df_05m,df_1m])
                print("Plot creation")
                var = df.melt(col_level = 0,id_vars=["doy","resolution"],value_vars=variable)
                var_ws = df_ws_doy.melt(col_level = 0,id_vars=["doy"],value_vars=variable)
                ax = sns.lineplot(data = var, x="doy", y="value",hue="resolution", linewidth = 2.5)
                ymin, ymax = ax.get_ylim()
                ax.set_title(f"Heino. {source} - Daily {variable.capitalize()} Irradiation", fontsize=fontBase)
                ax.set_xlabel("Day of year", fontsize=fontBase/1.5)
                ax.set_ylabel("Wh/m\u00b2", fontsize=fontBase/1.5)
                ax.set_xlim(0, 365)
                ax.set_xticks(range(0, 366, 5)) # <--- set the ticks first
                ax.set_xticklabels(range(0, 366, 5),fontsize = fontBase/3, rotation=45)
                ax.vlines(x=[31,59,90,120,151,181,212,243,273,304,334], ymin=ymin, ymax=ymax, colors="black", ls='-', lw=1)
                plt.legend(title='Spatial Resolution',title_fontsize=fontBase/2, fontsize = fontBase/3)
                plt.savefig(os.path.join(outputFolder,f'{source}-{variable}-ResolutionComparison.png'),dpi=250,bbox_inches='tight', transparent=True)
                print(f"Plot {source}-{variable}-ResolutionComparison.png Exported")
                plt.clf()
print("Script Ends")