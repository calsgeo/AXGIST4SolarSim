
@ECHO OFF
PUSHD %~dp0
REM SET SAGA_TLB=C:\MyTools
SET SAGA_CMD="c:\Users\Camilo\Dropbox\TUDelft\GitHub\AXGIST4SolarSim\Software\saga-8.5.1_x64\saga_cmd.exe"

REM Tool: Potential Incoming Solar Radiation

%SAGA_CMD% ta_lighting 2 ^
-GRD_DEM="c:\Users\Camilo\Dropbox\TUDelft\GitHub\AXGIST4SolarSim\Input_Data\Santana\outputRaster\geosampa_1m_dsm_124m_InputDEM_WSTA_Updated.tif" ^
-GRD_SVF="c:\Users\Camilo\Dropbox\TUDelft\GitHub\AXGIST4SolarSim\Results\Santana\SAGA GIS\Santana_1m_svf.tif" ^
-GRD_LINKE="c:\Users\Camilo\Dropbox\TUDelft\GitHub\AXGIST4SolarSim\Input_Data\Santana\outputRaster\Linke\Santana_1m_01_TL2010_Jan.tif" ^
-GRD_LINKE_DEFAULT=2.1 ^
-GRD_DIRECT="c:\Users\Camilo\Dropbox\TUDelft\GitHub\AXGIST4SolarSim\Results\Santana\SAGA GIS\Santana_1m_026_Direct Insolation.tif" ^
-GRD_DIFFUS="c:\Users\Camilo\Dropbox\TUDelft\GitHub\AXGIST4SolarSim\Results\Santana\SAGA GIS\Santana_1m_026_Diffuse Insolation.tif" ^
-GRD_TOTAL="c:\Users\Camilo\Dropbox\TUDelft\GitHub\AXGIST4SolarSim\Results\Santana\SAGA GIS\Santana_1m_026_Total Insolation.tif" ^
-GRD_DURATION="c:\Users\Camilo\Dropbox\TUDelft\GitHub\AXGIST4SolarSim\Results\Santana\SAGA GIS\Santana_1m_026_Duration of Insolation.tif" ^
-SOLARCONST=1367 ^
-LOCALSVF=1 ^
-UNITS=0 ^
-SHADOW=1 ^
-LOCATION="calculate from grid system" ^
-PERIOD=1 ^
-DAY="2022-01-26" ^
-DAY_STOP="2022-01-26" ^
-DAYS_STEP=1 ^
-HOUR_RANGE_MIN=0 ^
-HOUR_RANGE_MAX=24 ^
-HOUR_STEP=0.5 ^
-METHOD=3

PAUSE