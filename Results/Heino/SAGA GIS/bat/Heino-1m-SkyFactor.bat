
@ECHO OFF

PUSHD %~dp0

REM SET SAGA_TLB=C:\MyTools

SET SAGA_CMD=c:\Users\Camilo\Dropbox\TUDelft\GitHub\AXGIST4SolarSim\Software\saga-8.5.1_x64\saga_cmd.exe

REM Tool: Sky View Factor

%SAGA_CMD% ta_lighting 3 ^
-DEM="c:\Users\Camilo\Dropbox\TUDelft\GitHub\AXGIST4SolarSim\Input_Data\Heino\outputRaster\AHN_1m_dsm_1200m_InputDEM_WSTA_Updated.tif" ^
-VISIBLE="c:\Users\Camilo\Dropbox\TUDelft\GitHub\AXGIST4SolarSim\Results\Heino\SAGA GIS\Heino_1m_visible.tif" ^
-SVF="c:\Users\Camilo\Dropbox\TUDelft\GitHub\AXGIST4SolarSim\Results\Heino\SAGA GIS\Heino_1m_svf.tif" ^
-SIMPLE="c:\Users\Camilo\Dropbox\TUDelft\GitHub\AXGIST4SolarSim\Results\Heino\SAGA GIS\Heino_1m_simple.tif" ^
-TERRAIN="c:\Users\Camilo\Dropbox\TUDelft\GitHub\AXGIST4SolarSim\Results\Heino\SAGA GIS\Heino_1m_terrain.tif" ^
-DISTANCE="c:\Users\Camilo\Dropbox\TUDelft\GitHub\AXGIST4SolarSim\Results\Heino\SAGA GIS\Heino_1m_distance.tif" ^
-RADIUS=0 ^
-NDIRS=8 ^
-METHOD=1 ^
-DLEVEL=3

PAUSE
        