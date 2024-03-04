import pandas as pd
import os,sys
from timezonefinder import TimezoneFinder
import datetime
import pytz
import seaborn as sns
import matplotlib.pyplot as plt

year = datetime.date.today().year
folder = os.path.dirname(os.path.abspath('__file__'))
locations = ["Heino", "Santana"]
source = {"Heino":'KNMI', "Santana":'INMET'}
for location in locations:

    input_folder = os.path.join(folder,"Input_Data",location,"WeatherData")
    os.chdir(input_folder)
    output_Plotfolder = os.path.join(folder,"Results","plots")
    input_cols = ["ID []","Local []","Irradiance [W/m^2]","T_ambient [Degrees Celsius]","T_ground [Degrees Celsius]","Wind [m/s]","Cloud [okta]","Pressure [Pa]","Rain [mm/hr]","Diffuse [W/m^2]","Direct [W/m^2]","Elevation [Degrees]","Azimuth [Degrees]"]
    inputFile = f'{location}-hour.csv'
    
    df_hour = pd.read_csv(inputFile)
    df_day = df_hour[["GHI (W/m^2)","DNI (W/m^2)","DHI (W/m^2)"]].groupby(df_hour.index // 24).sum().reset_index()
    df_day["DOY"] = df_day.index + 1
    df_day["source"] = source[location]

    # set up for later plots
    fontBase = 50
    sns.set_theme( rc = {'figure.figsize' : ( 30, 10 )}, style='whitegrid', font_scale=2)

    # plot creation
    ax = sns.lineplot(data = df_day, x="DOY", y="GHI (W/m^2)", linewidth = 2,hue="source")
    ymin, ymax = ax.get_ylim()
    ax.set_title(f"{location}. Daily Global Irradiation", fontsize=fontBase)
    ax.set_xlabel("Day of year", fontsize=fontBase/1.5)
    ax.set_ylabel("Wh/m\u00b2", fontsize=fontBase/1.5)
    ax.set_xlim(0, 365)
    ax.set_xticks(range(0, 366, 5)) # <--- set the ticks first
    ax.set_xticklabels(range(0, 366, 5),fontsize = fontBase/3, rotation=45)
    ax.vlines(x=[31,59,90,120,151,181,212,243,273,304,334], ymin=ymin, ymax=ymax, colors="gray", ls='-', lw=1.5)
    plt.legend(frameon=True,fontsize = fontBase/5)
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    output_PlotFile = f'{location}-Weather-Global.png'
    output_PlotPath = os.path.join(output_Plotfolder,output_PlotFile)
    plt.savefig(output_PlotPath,dpi=250,bbox_inches='tight', transparent=True)
    print(f'File {output_PlotFile} created')
    plt.clf()
