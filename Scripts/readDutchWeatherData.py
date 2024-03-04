import pandas as pd
import os,sys
from timezonefinder import TimezoneFinder
import datetime
import pytz
import seaborn as sns
import matplotlib.pyplot as plt

def get_local_etc_timezone(latitude, longitude):
    # get the time zone at the given coordinates
    tf = TimezoneFinder()
    time = pytz.timezone(tf.timezone_at(lng=longitude, lat=latitude)).localize(
        datetime.datetime(2011, 1, 1)).strftime('%z')

    # invert sign and return in 'Etc/GMT' format
    if time[0] == '+':
        time_zone = '+' + time[2]
    else:
        time_zone = '-' + time[2]

    return time_zone

year = datetime.date.today().year
folder = os.path.dirname(os.path.abspath('__file__'))
input_folder = os.path.join(folder,"Input_Data","Heino","WeatherData")
output_folder = os.path.join(folder,"Input_Data","Heino","Vector")
os.chdir(input_folder)
input_cols = ["ID []","Local []","Irradiance [W/m^2]","T_ambient [Degrees Celsius]","T_ground [Degrees Celsius]","Wind [m/s]","Cloud [okta]","Pressure [Pa]","Rain [mm/hr]","Diffuse [W/m^2]","Direct [W/m^2]","Elevation [Degrees]","Azimuth [Degrees]"]
inputFile = 'Climate278.csv'
outputFile = 'Heino.csv'

count_line = 0
with open (inputFile, 'rt') as myfile:
    for myline in myfile:
        if count_line < 27:
            pass
        elif count_line == 27:
            cols = myline.strip().replace('"', '').split(',')
            df_weather = pd.DataFrame(columns=cols)
        elif count_line < 8812:
            myline = myline.strip().replace('"', '').split(",")
            df_length = len(df_weather)
            try:
                df_weather.loc[df_length] = myline
            except:
                print(f"{count_line}: Line with error")
        else:
            pass
        count_line +=1


# Convert the 'date_string' column to datetime
df_weather[['date', 'time']] = df_weather['Local []'].str.split(' ',expand=True)
df_weather['ID []'] = df_weather['ID []'].astype(int)
df_weather['hour'] = ((df_weather['ID []'] - 1) % 24) + 1
df_weather['month'] = df_weather['date'].str[5:7].astype(int)
df_weather['day'] = df_weather['date'].str[8:10].astype(int)

dm = ['dm']
df_dm = pd.DataFrame(columns=dm)
df_citysim = pd.DataFrame().assign(dm=df_weather['day'], m=df_weather['month'], h=df_weather['hour'], G_Dh=df_weather['Diffuse [W/m^2]'], G_Bn=df_weather['Direct [W/m^2]'], Ta=df_weather['T_ambient [Degrees Celsius]'], Ts=df_weather['T_ground [Degrees Celsius]'], FF=df_weather['Wind [m/s]'], DD= [0]*8784, RH=[0]*8784, RR=df_weather['Rain [mm/hr]'], N=df_weather['Cloud [okta]'])

WMOCode = ''
city = 'Heino'
stateProv = ''
latitude = 52.4344
longitude = 6.2589
altitude = 3.6
timeZone = str(get_local_etc_timezone(latitude, longitude))

# CitySim Weather file creation
header_1 = city
header_2 = str(latitude)+ "," +str(longitude)+ "," + str(altitude)+ ","  + timeZone

output = os.path.join(output_folder,"Heino_CitySimData",f"{header_1}.cli")

filtered_df = df_citysim[~df_citysim.index.isin(range(1418, 1442))]

with open(output, "w") as outfile:
    outfile.write(header_1)
    outfile.write("\n")
    outfile.write(header_2)
    outfile.write("\n")
    outfile.write("\n")
filtered_df.to_csv(output, mode='a', index=False, header=True, sep='\t', float_format='%g')
filtered_df['G_Bn'].to_csv(os.path.join(output_folder,'Direct_Heino.csv'), index=False,header=False)
filtered_df['G_Dh'].to_csv(os.path.join(output_folder,'Diffuse_Heino.csv'), index=False,header=False)

print(f"The script finishes. File {header_1}.cli was created")


tmy_cols = ['Date (MM/DD/YYYY)','Time (HH:MM)','ETR (W/m^2)','ETRN (W/m^2)','GHI (W/m^2)','GHI source','GHI uncert (%)','DNI (W/m^2)','DNI source','DNI uncert (%)','DHI (W/m^2)','DHI source','DHI uncert (%)','GH illum (lx)','GH illum source','Global illum uncert (%)','DN illum (lx)','DN illum source','DN illum uncert (%)','DH illum (lx)','DH illum source','DH illum uncert (%)','Zenith lum (cd/m^2)','Zenith lum source','Zenith lum uncert (%)','TotCld (tenths)','TotCld source','TotCld uncert (code)','OpqCld (tenths)','OpqCld source','OpqCld uncert (code)','Dry-bulb (C)','Dry-bulb source','Dry-bulb uncert (code)','Dew-point (C)','Dew-point source','Dew-point uncert (code)','RHum (%)','RHum source','RHum uncert (code)','Pressure (mbar)','Pressure source','Pressure uncert (code)','Wdir (degrees)','Wdir source','Wdir uncert (code)','Wspd (m/s)','Wspd source','Wspd uncert (code)','Hvis (m)','Hvis source','Hvis uncert (code)','CeilHgt (m)','CeilHgt source','CeilHgt uncert (code)','Pwat (cm)','Pwat source','Pwat uncert (code)','AOD (unitless)','AOD source','AOD uncert (code)','Alb (unitless)','Alb source','Alb uncert (code)','Lprecip depth (mm)','Lprecip quantity (hr)','Lprecip source','Lprecip uncert (code)']
df_tmy = pd.DataFrame(columns=tmy_cols)

df_tmy['Date (MM/DD/YYYY)'] = df_weather.apply(lambda x: str(x['month']).zfill(2) + "/" + str(x['day']).zfill(2) + "/" + str(year).zfill(4),axis=1)
df_tmy['Time (HH:MM)'] = df_weather.apply(lambda x: str(x['hour']).zfill(2) + ":" + str(0).zfill(2),axis=1)
df_tmy['GHI (W/m^2)'] = df_weather["Irradiance [W/m^2]"]
df_tmy['DNI (W/m^2)'] = df_weather["Direct [W/m^2]"]
df_tmy['DHI (W/m^2)'] = df_weather["Diffuse [W/m^2]"]
df_tmy['Dry-bulb (C)'] = df_weather["T_ambient [Degrees Celsius]"]
df_tmy['Pressure (mbar)'] = pd.to_numeric(df_weather["Pressure [Pa]"])/100
df_tmy['TotCld (tenths)'] = pd.to_numeric(df_weather["Cloud [okta]"])*1.25
df_tmy['Wspd (m/s)'] = df_weather["Wind [m/s]"]
df_tmy['Pwat (cm)'] = pd.to_numeric(df_weather["Rain [mm/hr]"])*10

df_tmy[['ETR (W/m^2)', 'ETRN (W/m^2)', 'GH illum (lx)', 'DN illum (lx)', 'DH illum (lx)', 'Zenith lum (cd/m^2)', 'OpqCld (tenths)', 'Dew-point (C)', 'RHum (%)', 'Wdir (degrees)', 'Hvis (m)', 'CeilHgt (m)', 'AOD (unitless)', 'Alb (unitless)', 'Lprecip depth (mm)', 'Lprecip quantity (hr)', "GHI source", "GHI uncert (%)", "DNI source", "DNI uncert (%)", "DHI source", "DHI uncert (%)", "GH illum source" ,"Global illum uncert (%)" , "DN illum source", "DN illum uncert (%)" , "DH illum source", "DH illum uncert (%)", "Zenith lum source", "Zenith lum uncert (%)", "TotCld source" ,"TotCld uncert (code)", "OpqCld source", "OpqCld uncert (code)", "Dry-bulb source", "Dry-bulb uncert (code)", "Dew-point source", "Dew-point uncert (code)", "RHum source", "RHum uncert (code)", "Pressure source", "Pressure uncert (code)", "Wdir source", "Wdir uncert (code)", "Wspd source", "Wspd uncert (code)", "Hvis source", "Hvis uncert (code)", "CeilHgt source", "CeilHgt uncert (code)", "Pwat (cm)", "Pwat source", "Pwat uncert (code)", "AOD source", "AOD uncert (code)", "Alb source", "Alb uncert (code)", "Lprecip source", "Lprecip uncert (code)"]] = 0

df_tmy.rename(columns={'ETR (W/m^2)': 'NaN', 'ETRN (W/m^2)': 'NaN', 'GH illum (lx)': 'NaN', 'DN illum (lx)': 'NaN', 'DH illum (lx)': 'NaN', 'Zenith lum (cd/m^2)': 'NaN', 'OpqCld (tenths)': 'NaN', 'Dew-point (C)': 'NaN', 'RHum (%)': 'NaN', 'Wdir (degrees)': 'NaN', 'Hvis (m)': 'NaN', 'CeilHgt (m)': 'NaN', 'AOD (unitless)': 'NaN', 'Alb (unitless)': 'NaN', 'Lprecip depth (mm)': 'NaN', 'Lprecip quantity (hr)': 'NaN', "GHI source": 'NaN', "GHI uncert (%)": 'NaN', "DNI source": 'NaN', "DNI uncert (%)": 'NaN', "DHI source": 'NaN', "DHI uncert (%)": 'NaN', "GH illum source": 'NaN' ,"Global illum uncert (%)": 'NaN' , "DN illum source": 'NaN', "DN illum uncert (%)": 'NaN' , "DH illum source": 'NaN', "DH illum uncert (%)": 'NaN', "Zenith lum source": 'NaN', "Zenith lum uncert (%)": 'NaN', "TotCld source": 'NaN' ,"TotCld uncert (code)": 'NaN', "OpqCld source": 'NaN', "OpqCld uncert (code)": 'NaN', "Dry-bulb source": 'NaN', "Dry-bulb uncert (code)": 'NaN', "Dew-point source": 'NaN', "Dew-point uncert (code)": 'NaN', "RHum source": 'NaN', "RHum uncert (code)": 'NaN', "Pressure source": 'NaN', "Pressure uncert (code)": 'NaN', "Wdir source": 'NaN', "Wdir uncert (code)": 'NaN', "Wspd source": 'NaN', "Wspd uncert (code)": 'NaN', "Hvis source": 'NaN', "Hvis uncert (code)": 'NaN', "CeilHgt source": 'NaN', "CeilHgt uncert (code)": 'NaN', "Pwat (cm)": 'NaN', "Pwat source": 'NaN', "Pwat uncert (code)": 'NaN', "AOD source": 'NaN', "AOD uncert (code)": 'NaN', "Alb source": 'NaN', "Alb uncert (code)": 'NaN', "Lprecip source": 'NaN', "Lprecip uncert (code)": 'NaN'}, inplace=True)

filtered_tmy = df_tmy[~df_tmy.index.isin(range(1418, 1442))].reset_index()


headerSimStadt = f"{WMOCode},{city},{stateProv},{timeZone},{latitude},{longitude},{altitude}"
fileName = f"{city}-hour"
outputSimStadt = os.path.join(output_folder,fileName + ".tmy3")
outputCSV = os.path.join(input_folder, fileName + ".csv")

with open(outputSimStadt, "w") as outfile:
    outfile.write(headerSimStadt)
    outfile.write("\n")
filtered_tmy.to_csv(outputSimStadt, mode='a', index=False, header=True, sep=',', float_format='%g')
filtered_tmy.to_csv(outputCSV, index=False, header=True, sep=',', float_format='%g')

print(f"The script finishes. File {fileName} was created")

filtered_tmy[["GHI (W/m^2)","DNI (W/m^2)","DHI (W/m^2)"]] = filtered_tmy[["GHI (W/m^2)","DNI (W/m^2)","DHI (W/m^2)"]].apply(pd.to_numeric)


filtered_day = filtered_tmy[["GHI (W/m^2)","DNI (W/m^2)","DHI (W/m^2)"]].groupby(filtered_tmy.index // 24).sum().reset_index()
filtered_day["DOY"] = filtered_day.index + 1

# set up for later plots
fontBase = 50
sns.set_theme( rc = {'figure.figsize' : ( 30, 10 )}, style='whitegrid', font_scale=2)

# plot creation
ax = sns.lineplot(data = filtered_day, x="DOY", y="GHI (W/m^2)", linewidth = 2)
ymin, ymax = ax.get_ylim()
ax.set_title(f"Heino. Daily Global Irradiation", fontsize=fontBase)
ax.set_xlabel("Day of year", fontsize=fontBase/1.5)
ax.set_ylabel("Wh/m\u00b2/d", fontsize=fontBase/1.5)
ax.set_xlim(0, 365)
ax.set_xticks(range(0, 366, 5)) # <--- set the ticks first
ax.set_xticklabels(range(0, 366, 5),fontsize = fontBase/3, rotation=45)
ax.vlines(x=[31,59,90,120,151,181,212,243,273,304,334], ymin=ymin, ymax=ymax, colors="gray", ls='-', lw=1.5)
plt.legend(frameon=True,fontsize = fontBase/5)
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
output_PlotFile = 'Heino-Weather-Global.png'
output_Plotfolder = os.path.join(folder,"Results","plots")
output_PlotPath = os.path.join(output_Plotfolder,output_PlotFile)

plt.savefig(output_PlotPath,dpi=250,bbox_inches='tight', transparent=True)