#!/usr/bin/env python3

import grass.script as gscript
import sys

location = 'Santana' # options: 'Heino' and 'Santana'
resolution = "1m" # For Heino: '05m' or '1m'. For Santana: '1m'

if location == 'Heino':
    dataSource = 'AHN'
    distance = 1200
elif location == 'Santana':
    dataSource = 'geosampa'
    distance = 124
else:
    print(f'Unexpected location: {location}')
    sys.exit()

def compute_r_sun(i):
    day_value = str(i).zfill(3)
    glob_rad_value = location + "-" + resolution +  "-" + day_value + "-" + "glob_rad"
    beam_rad_value = location + "-" + resolution +  "-" + day_value + "-" + "beam_rad"
    diff_rad_value = location + "-" + resolution +  "-" + day_value + "-" + "diff_rad"
    refl_rad_value = location + "-" + resolution +  "-" + day_value + "-" + "refl_rad"
    if i<=31:
        linke_value = 2.1
        linke = "{}_{}_01_TL2010_Jan".format(location,resolution)
    elif i<=59:
        linke_value = 2.2
        linke = "{}_{}_02_TL2010_Feb".format(location,resolution)
    elif i<=90:
        linke_value = 2.5
        linke = "{}_{}_03_TL2010_Mar".format(location,resolution)
    elif i<=120:
        linke_value = 2.9
        linke = "{}_{}_04_TL2010_Apr".format(location,resolution)
    elif i<=151:
        linke_value = 3.2
        linke = "{}_{}_05_TL2010_May".format(location,resolution)
    elif i<=181:
        linke_value = 3.4
        linke = "{}_{}_06_TL2010_Jun".format(location,resolution)
    elif i<=212:
        linke_value = 3.5
        linke = "{}_{}_07_TL2010_Jul".format(location,resolution)
    elif i<=243:
        linke_value = 3.3
        linke = "{}_{}_08_TL2010_Aug".format(location,resolution)
    elif i<=273:
        linke_value = 2.9
        linke = "{}_{}_09_TL2010_Sep".format(location,resolution)
    elif i<=304:
        linke_value = 2.6
        linke = "{}_{}_10_TL2010_Oct".format(location,resolution)
    elif i<=334:
        linke_value = 2.3
        linke = "{}_{}_11_TL2010_Nov".format(location,resolution)
    else:
        linke_value = 2.2
        linke = "{}_{}_12_TL2010_Dec".format(location,resolution)

    gscript.run_command("r.sun",
    overwrite = True,
    elevation = f"{dataSource}_{resolution}_dsm_{distance}m_InputDEM_WSTA_Updated",
    aspect = f"aspect_{location}_{resolution}",
    slope = f"slope_{location}_{resolution}",
    horizon_basename = f"horizon_{location}_{resolution}",
    linke = linke,
    horizon_step=3,
    glob_rad=glob_rad_value,
    beam_rad=beam_rad_value,
    diff_rad=diff_rad_value,
    refl_rad=refl_rad_value,
    day=i,
    step=0.5,
    nprocs=64,
    npartitions=2
    )

if __name__ == '__main__':
    for i in range(1,366):
        compute_r_sun(i)