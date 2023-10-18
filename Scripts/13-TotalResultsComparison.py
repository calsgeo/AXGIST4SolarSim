import pandas as pd
import seaborn as sns
import os,sys
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import glob

def get_month(x):
    if x<= 31: month= 1
    elif x<= 59: month= 2
    elif x<= 90: month= 3
    elif x<= 120: month= 4
    elif x<= 151: month= 5
    elif x<= 181: month= 6
    elif x<= 212: month= 7
    elif x<= 243: month= 8
    elif x<= 273: month= 9
    elif x<= 304: month= 10
    elif x<= 334: month= 11
    else: month= 12
    return month

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

def comparison_cal(values, observation):
    values_array = np.array(values)/1000
    observation_array = np.array(observation)/1000
    diff = np.round(((np.sum(observation_array) - (np.sum(values_array)))/np.sum(values_array)),4)
    rmse = np.round(np.square(np.subtract(values_array, observation_array)).mean(),3)
    total = np.round(np.sum(observation_array),3)
    return total,diff,rmse

time_start = datetime.now()

print(f"Script starts")

root_folder = os.path.normpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
locationList = ['Heino','Santana']
sourcesList = ["ArcGISPro",'CitySim',"GRASS GIS",'Ladybug',"SAGA GIS",'SimStadt']
list_variables = ["global","direct","diffuse"]


for location in locationList:
    weatherFolder = os.path.join(root_folder,'Input_Data',location,'WeatherData')
    inputFolder = os.path.join(root_folder,'Results',location,'csv')
    outputFolder = os.path.join(root_folder,'Results','plots')
    if location == 'Heino':
        weatherFileName = "NLD_OV_Heino.062780_TMYx.2007-2021.csv"
        df_umep = pd.DataFrame( {'variable':['UMEP'], 'value':1046.2833} ) #UMEP data
        sourceName = 'oneBuilding'
        sourcesDict = {"ArcGISPro":'05m','CitySim':'1m',"GRASS GIS":'05m','Ladybug':'1m',"SAGA GIS":'05m','SimStadt':'1m'}
    else:
        weatherFileName = "Santana_EPW_SimStadt.csv"
        df_umep = pd.DataFrame( {'variable':['UMEP'], 'value':1233.7388} ) #UMEP data
        sourceName = 'INMET'
        sourcesDict = {"ArcGISPro":'1m','CitySim':'1m',"GRASS GIS":'1m','Ladybug':'1m',"SAGA GIS":'1m','SimStadt':'1m'}
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
        df_ws_doy["source"] = sourceName
        df_ws_doy = df_ws_doy.rename(columns={'GHI (W/m^2)':"global",'DNI (W/m^2)':"direct",'DHI (W/m^2)':"diffuse"})
        sum_WD = np.sum(df_ws_doy['global'].values)/1000 # Yearly value of global irradiance
    fontBase = 50
    sns.set( rc = {'figure.figsize' : ( 30, 10 )}, style='whitegrid', font_scale=2)

    df_graph = pd.DataFrame(columns=['doy','global','source'])
    df_total = pd.DataFrame(columns=['doy'])
    df_total['doy'] = df_ws_doy.index + 1
    for source in sourcesList:
        file = os.path.join(inputFolder,f'{source}-{sourcesDict[source]}-SimulationResults.csv')
        isExist = os.path.exists(file)
        if isExist:
            df = pd.read_csv(file)
            columns_list = df.columns.values.tolist()
            if 'global' not in columns_list:
                df['global'] = df['RoofSurface']
            df['source'] = source
            df_total[source] = df['global']
            df_graph = pd.concat([df_graph,df], join = 'inner')
        else:
            print(f'File {source} is not available')
            pass
    colours = ['#e41a1c','#377eb8','#4daf4a','#ff7f00','#984ea3','#ffff33',"#000000"] #PrintFriendly
    colours_bar = ['#e41a1c','#377eb8','#4daf4a','#ff7f00','#984ea3','#ffff33','#a65628',"#000000"]
    # Set your custom colour palette
    customPalette = sns.set_palette(sns.color_palette(colours))
    customPalette_bar = sns.color_palette(colours_bar)

    df_total['Weather data'] = df_ws_doy['global']
    # df_total.rename(columns={'ArcGISPro':"ArcGIS"}, inplace=True)
    df_total = df_total.reindex(sorted(df_total.columns), axis=1)
    df_total["month"] = list(map(get_month, df_total['doy']))

    sim_tools = ["ArcGIS", "GRASS GIS", "SAGA GIS", "SimStadt",'CitySim', 'Ladybug']
    df_total_m = df_total.groupby('month').sum()/1000
    del[df_total_m['doy']]
    df_total_m = df_total_m.reset_index()
    
    annual_total, annual_diff, annual_rmse, annual_dict = [], [], [], {}
    month_simTools, month_list, monthly_total, monthly_diff, monthly_rmse, monthly_dict = [], [], [], [], [], {}

    for x in sourcesList:
        total_x, diff_x, rmse_x = comparison_cal(df_total['Weather data'], df_total[x])
        annual_total.append(total_x), annual_diff.append(diff_x), annual_rmse.append(rmse_x)
        for m in range(1,13):
            df_m = df_total[df_total['month'] == m]
            total_m, diff_m, rmse_m = comparison_cal(df_m['Weather data'], df_m[x])
            monthly_total.append(total_m), monthly_diff.append(diff_m), monthly_rmse.append(rmse_m), month_list.append(m), month_simTools.append(x)

    annual_dict['source'] = sourcesList
    annual_dict['total'] = annual_total
    annual_dict['diff'] = annual_diff
    annual_dict['rmse'] = annual_rmse

    monthly_dict['month'] = month_list
    monthly_dict['diff'] = monthly_diff
    monthly_dict['rmse'] = monthly_rmse
    monthly_dict['total'] = monthly_total
    monthly_dict['source'] = month_simTools


    annual_df = pd.DataFrame.from_dict(annual_dict)
    annual_df_transposed = annual_df.T
    monthly_df = pd.DataFrame.from_dict(monthly_dict)
    # outputFolder = os.path.join(root_folder,"output","csv")
    outfile_annual = f'{location}_annual_values.csv'
    outfile_monthly = f'{location}_monthly_values.csv'
    outputFile_annual = os.path.join(inputFolder,outfile_annual)
    outputFile_month = os.path.join(inputFolder,outfile_monthly)
    annual_df_transposed.to_csv(outputFile_annual,index=False)
    monthly_df.to_csv(outputFile_month,index=False)

    print("Plots creation")

    ######## Monthly Analysis
    var_m = df_total_m.melt(col_level = 0,id_vars=["month"],value_vars=['ArcGISPro','CitySim','GRASS GIS','Ladybug','SAGA GIS','SimStadt','Weather data'])
    var_m = pd.concat([var_m,df_umep])
    var_m = var_m.sort_values(by=['variable','month'])

    # var_m = df_total_m.melt(col_level = 0,id_vars=["month"],value_vars=source_list)
    ax_m = sns.barplot(data=var_m, x="variable", y="value", errorbar=None, estimator=sum, palette=customPalette_bar, linewidth=0)
    ax_m.axhline(sum_WD, color = 'black',linestyle='--')
    ax_m.set_title(f"{location}. Yearly Global Solar Irradiation", fontsize=fontBase)
    ax_m.set_xlabel("Simulation Tool", fontsize=fontBase/1.5)
    ax_m.set_ylabel("kWh/m\u00b2", fontsize=fontBase/1.5)
    ax_m.bar_label(ax_m.containers[0], fontsize=fontBase/2, weight='bold' )
    outputPlotFile = f'{location}-AllSimulations-AnnualComparison.png'
    plt.savefig(os.path.join(outputFolder,f'{outputPlotFile}'),dpi=250,bbox_inches='tight', transparent=True)
    print(f"Plot {outputPlotFile} Exported")
    plt.clf()


    ######## Daily Analysis
    df_graph = pd.concat([df_graph,df_ws_doy[["doy","global","source"]]], join = 'inner')
    df_graph =df_graph.sort_values(['doy','source'], ascending=[True, True])
    df_graph['source'] = np.where(df_graph['source'] == sourceName, 'Weather Data', df_graph['source'])
    var = df_graph.melt(col_level = 0,id_vars=["doy","source"],value_vars='global')
    var =var.sort_values(['source','doy'], ascending=[True, True])
    var =var.reset_index(drop=True)

    ax = sns.lineplot(data = var, x="doy", y="value",hue="source", linewidth = 2, palette=customPalette)

    ymin, ymax = ax.get_ylim()
    ax.set_title(f"{location}. Daily global solar irradiation", fontsize=fontBase)
    ax.set_xlabel("Day of year", fontsize=fontBase/1.5)
    ax.set_ylabel("Wh/m\u00b2", fontsize=fontBase/1.5)
    ax.set_xlim(0, 365)
    ax.set_xticks(range(0, 366, 5)) # <--- set the ticks first
    ax.set_xticklabels(range(0, 366, 5),fontsize = fontBase/3, rotation=45)
    ax.vlines(x=[31,59,90,120,151,181,212,243,273,304,334], ymin=ymin, ymax=ymax, colors="gray", ls='-', lw=1.5)
    plt.legend(frameon=True,fontsize = fontBase/5)
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    outputPlotFile = f'{location}-AllSimulations-Comparison.png'
    plt.savefig(os.path.join(outputFolder,f'{outputPlotFile}'),dpi=250,bbox_inches='tight', transparent=True)
    print(f"Plot {outputPlotFile} Exported")
    plt.clf()

print("Script Ends")