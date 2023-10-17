# AXGIST4SolarSim
This repository contains the material (scripts and data) for the paper titled assessment of geospatial tools for solar simulation

The followed workflow of our research can be seen in the following image:
<center>
<img src="images/workflow.png " width="400" height="320">
</center>
The data collection section is split into two test sites: Santana in Brazil and Heino in the Netherlands. The required data is described inside the folder Input_Data of this repository.

## Input_Data
This folder contains the folders *Heino* and *Santana*. In those subfolder there are available the necessary data for this project. The basic structure in each folder is the following:

- **baseRaster:** This folder contains the raster files downloaded from the data sources used for this research. Those files are the starting point for our workflow. Due to storage restrictions, we place the download link to the corresponding repository.

    In the specific case of the DSM published by the Copernicus project, we noted that the data is no longer available to download at the time of creating this repository [September-October 2023] [more info here](https://land.copernicus.eu/en/products/products-that-are-no-longer-disseminated-on-the-clms-website?tag=Copernicus%20Land), so we are including a small excerpt of the dataset to users can use them in a similar way as we have done in this research.

- **csv:** This folder stores the files created to compute the horizon file and the corresponding graphs.
- **outputRaster:** This folder contains the results of the first 7 Python scripts. These files are the input for the corresponding raster-based simulation tool.

    For the case of Urban Multi-scale Environmental Predictor (UMEP) we decided to provide the data already prepared due to its requirements:
    - A raster-based DSM that contains the terrain and building features,
    - A raster file that contains the location of trees.

    Each of those files in the corresponding folder are named with the suffix "UMEP" to differentiated them from the other datasets.
- **Vector:** Contains the location of the weather station, as well as the the data for the corresponding vector-based simulation tool. Since the creation of these datasets are out of the scope of this research, we provide them directly so the user can test them in the corresponding software tool:
    - CitySim: CitySim XML & CLI climate file,
    - Ladybug: An 3dm file with a grasshopper file,
    - SimStadt: A CityGML file.

## Scripts
This folder contains all the scripts necessary. There are subfolders for each of the test sites and they prepare the raster data according to the requirements of the corresponding simulation tool. All scripts have been adjusted to manage the relative path from this repository.

Script files have the following structure {testSiteName}_{sequentialNumber}_{scriptName}.py. All scripts inside this folder follow the same sequential number and name. However, it can be the case that one specific file does not exits: this is because the script was not necessary for that location, i.e., **Santana_1_mergeRaster**.

At the root of this folder you find the scripts necessary for results consolidation, plotting and analysis. These scripts continue with the sequential number from the location subfolders. The following paragraphs describe the scripts mentioning only the sequential number.

Scripts 1 to 8 shall be execute for the data preparation that will be used in the raster-based software tools. The Python files to execute the raster-based software tools are stored in the folder SoftwareTools.

- Scripts **1 - 7:** prepare the input DSM files for the software simulation tools.

From script **8**, all of them take care of each of the location.

- Script **8:** creates the Linke turbidity files with the same spatial resolution as the input DSM from for the two study areas.
- Script **9:** consolidates the results from (GRASS GIS and SAGA GIS) from several raster files into a single one with 365 raster bands corresponding to the day of the year.
- Script **10A & 10B:** These scripts create a csv file for each simulation tool with the consolidated results per day.
- Script **11:** This script creates the line plots to compare the results of the raster-based simulation tools in Heino.

### SoftwareTools
It contains:
-  **ArcGISPro.py:** This script shall be execute in a Python environment for ArcGIS Pro 3.X,
- **GRASS_1_script.md:** This file contains the console scripts import and create the necessary files to run the r.sun in GRASS 7.8.
    - The data to import are the DSM and the Linke Turbidity files.
-  **GRASS_2_rsun.py** This Python script shall be execute inside the GRASS environment. It calls the tool *r.sun* which simulates the solar irradiance for the data imported and prepared based on file *GRASS_script.md*. The simulation is execute for the 365 days of a typical year. In this file, the user needs to update the following lines:
    - **6:** To indicate the site location. Options are *Heino* or *Santana*.
    - **7:** To indicate the spatial resolution. Options are *05m* or *1m*.
- **GRASS_3_exportRaster.py** This Python script shall be execute to export the results of *r.sun*. In this file, the user needs to update the following lines:
    - **12:** To indicate the site location. Options are *Heino* or *Santana*.
    - **13:** To indicate the spatial resolution. Options are *05m* or *1m*.
    - **14:** To indicate the root path for the output files. Please indicate the path to the main folder of this repository.
- **SAGAGIS_1_SkyFactor.py** This Python script creates a batch file to execute in a Windows environment to create the solar sky factor file from the input DSM. The output patch file points to the path of the decompressed file *saga-8.5.1_x64.zip*, which is located in the Software folder.

- **SAGAGIS_2_SolarBatFiles.py** This Python script creates the 365 batch files to execute the solar insolation tool from SAGA GIS. It requires the sky factor raster file created by the execution of the resulting batch file from *SAGAGIS_1_SkyFactor.py*; additionaly, it requires as well, the Linke turbidity files created by scripts number 8 for the corresponding location.
## Software
This folder contains the executables for some of the software used in this research such as:
- **SAGA GIS:** File *saga-8.5.1_x64.zip* [Download link](https://sourceforge.net/projects/saga-gis/files/SAGA%20-%208/SAGA%20-%208.5.1/). Scripts and simulations were done using the software for Windows x64 version 8.5.1.
- **CitySim Solver:** File *CitySimSolver.zip* [Download link](https://github.com/kaemco/CitySim-Solver). Compiled for Windows in June 5 2023.